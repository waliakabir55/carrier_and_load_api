from pydantic import BaseSettings
from typing import List, Union
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    api_key: str
    fmcsa_api_key: str
    allowed_origins: Union[str, List[str]] = ["*"]
    DATABASE_URL: str = ""
    
    # Proxy specific configuration
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 2
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    
    class Config:
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()