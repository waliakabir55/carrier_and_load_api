from sqlalchemy import Column, String, Numeric, DateTime
from sqlalchemy.sql import func
from .database import Base

from sqlalchemy import Column, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Load(Base):
    __tablename__ = "loads"
    
    reference_number = Column(String, primary_key=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    equipment_type = Column(String, nullable=False)
    rate = Column(Float, nullable=False)
    commodity = Column(String, nullable=False)

    class Config:
        orm_mode = True