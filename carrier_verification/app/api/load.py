from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging
from ..db.database import get_db
from ..db.models import Load
from ..config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """
    Verify the API key provided in the request headers.

    If the API key is invalid, an HTTPException with status code 403 is raised.
    If the API key is valid, the API key is returned.

    Parameters:
        api_key (str): The API key for authentication.

    Returns:
        str: The API key if it is valid.

    Raises:
        HTTPException: If the API key is invalid.
    """
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    return api_key

@router.get("/loads/{reference_number}")
@router.get("/loads/")
async def get_load(
    reference_number: str = None, 
    db: Session = Depends(get_db), 
    api_key: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    Retrieve load details based on the provided reference number.
    The reference number can be provided as a path parameter or a query parameter.

    This endpoint allows users to fetch details of a specific load by its 
    reference number. If the reference number is not provided, the request 
    will return an error. The reference number must be alphanumeric and 
    will be converted to uppercase for consistency.

    Parameters:
        reference_number (str): The unique identifier for the load. 
                                Must be alphanumeric.
        db (Session): The database session dependency for querying the database.
        api_key (str): The API key for authentication.

    Returns:
        Dict[str, Any]: A dictionary containing the load details, including:
            - reference_number (str): The reference number of the load.
            - origin (str): The origin location of the load.
            - destination (str): The destination location of the load.
            - equipment_type (str): The type of equipment required for the load.
            - rate (float): The rate for transporting the load.
            - commodity (str): The type of commodity being transported.

    Raises:
        HTTPException: 
            - 400: If the reference number is invalid (non-alphanumeric).
            - 404: If no load is found for the provided reference number.
            - 500: If an internal server error occurs during the retrieval process.
    """

    if reference_number is not None:
        if not reference_number.isalnum():
            logger.warning(f"Invalid reference number: {reference_number}")
            raise HTTPException(status_code=400, detail="Reference number must be alphanumeric")
        reference_number = reference_number.upper()

    try:
        logger.info(f"Retrieving load details for: {reference_number}")
        load = db.query(Load).filter(Load.reference_number == reference_number).first()
        
        if load is None:
            logger.warning(f"Load not found: {reference_number}")
            raise HTTPException(status_code=404, detail=f"The reference number {reference_number} was not found. Please check the reference number and try again.")
            
        return {
            "reference_number": load.reference_number,
            "origin": load.origin,
            "destination": load.destination,
            "equipment_type": load.equipment_type,
            "rate": float(load.rate), 
            "commodity": load.commodity
        }
    except Exception as e:
        logger.error(f"Error retrieving load: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")