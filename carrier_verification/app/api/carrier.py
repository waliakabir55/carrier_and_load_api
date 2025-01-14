from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from typing import Dict, Any
import requests
import logging
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

@router.get("/verify_carrier/{mc_number}")
@router.get("/verify_carrier/")
async def verify_carrier(
    mc_number: str = None,
    api_key: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    Verify a carrier using their MC number through the FMCSA API.

    This endpoint allows users to verify the status of a carrier by 
    providing their Motor Carrier (MC) number. The function checks 
    the carrier's operational status and retrieves relevant details 
    from the FMCSA API.

    Parameters:
        mc_number (str): The Motor Carrier number to verify. 
                         This is required as a path or query parameter.
        api_key (str): The API key for authentication.

    Returns:
        Dict[str, Any]: A dictionary containing the verification result and carrier details, including:
            - verified (bool): Indicates if the carrier is verified and active.
            - message (str): A message describing the verification result.
            - details (dict): Additional information about the carrier, including:
                - mc_number (str): The provided MC number.
                - allowed_to_operate (bool): Indicates if the carrier is allowed to operate.
                - status_code (str): The current status code of the carrier.
                - legal_name (str): The legal name of the carrier.
                - dba_name (str): The "Doing Business As" name of the carrier.
                - dot_number (str): The Department of Transportation number of the carrier.
                - address (dict): The physical address of the carrier, including:
                    - street (str): The street address.
                    - city (str): The city.
                    - state (str): The state.
                    - zip (str): The ZIP code.

    Raises:
        HTTPException: 
            - 400: If the MC number is not provided.
            - 500: If there is an issue with the FMCSA API key or during the API request.
    """

    if not mc_number:
        raise HTTPException(
            status_code=400,
            detail="MC number is required as a path parameter or query parameter"
        )

    logger.info(f"Received request for MC number: {mc_number}")

    if not settings.fmcsa_api_key:
        raise HTTPException(
            status_code=500,
            detail="FMCSA API key not configured"
        )

    url = f"https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/{mc_number}?webKey={settings.fmcsa_api_key}"

    
    try:
        # Log the exact request we're about to make
        logger.info(f"Making request to FMCSA API with URL: {url}")

        response = requests.get(
            url,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=30
        )

        # Log the response details
        logger.info(f"FMCSA API Response Status Code: {response.status_code}")
        logger.info(f"FMCSA API Response Headers: {dict(response.headers)}")
        logger.info(f"FMCSA API Response Content: {response.text}")
        
        response.raise_for_status()
        data = response.json()

        logger.info(f"Parsed JSON data: {data}")
        
        # Check if content exists and has carrier data
        if not data.get('content') or not data['content'] or not data['content'][0].get('carrier'):
            logger.info(f"Carrier not found for MC number: {mc_number}")
            return {
                "verified": False,
                "message": "Carrier not found",
                "details": {"mc_number": mc_number}
            }
            
        # Extract carrier data
        carrier = data['content'][0]['carrier']

        # Check if carrier is allowed to operate
        allowed_to_operate = carrier.get('allowedToOperate', 'N').upper() == 'Y'

        # Check if carrier is active
        status_code = carrier.get('statusCode', '').upper()
        
        # Define verified as true if carrier is allowed to operate AND is active
        is_verified = allowed_to_operate and status_code == 'A'
        
        return {
            "verified": is_verified,
            "message": "Carrier verified and active" if is_verified else "Carrier not active or not allowed to operate",
            "details": {
                "mc_number": mc_number,
                "allowed_to_operate": allowed_to_operate,
                "status_code": status_code,
                "legal_name": carrier.get('legalName', ''),
                "dba_name": carrier.get('dbaName', ''),
                "dot_number": carrier.get('dotNumber', ''),
                "address": {
                    "street": carrier.get('phyStreet', ''),
                    "city": carrier.get('phyCity', ''),
                    "state": carrier.get('phyState', ''),
                    "zip": carrier.get('phyZipcode', '')
                }
            }
        }
            
    except requests.exceptions.RequestException as e:
        logger.error(f"FMCSA API request failed: {str(e)}")
        logger.error(f"Exception details: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error verifying carrier: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )