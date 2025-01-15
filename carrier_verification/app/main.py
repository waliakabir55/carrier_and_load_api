import logging

# Configure root logger
root_logger = logging.getLogger()
if root_logger.handlers:
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

# Set up logging format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import logging
from .config import settings
from .api import carrier, load
from .db.database import get_db
from sqlalchemy import text
from fastapi import HTTPException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Carrier Verification and Load Management API",
    description="API for carrier verification and load management",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(carrier.router, prefix="/api/v1", tags=["carrier"])
app.include_router(load.router, prefix="/api/v1", tags=["load"])

@app.get("/", tags=["health"])
async def root():
    return {"message": "Welcome to Carrier Verification API"}

@app.get("/health", tags=["health"])
async def health_check():
    try:
        # Test database connection
        db = next(get_db())
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Lambda handler
handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)