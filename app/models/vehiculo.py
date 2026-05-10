from sqlalchemy import Column, Integer, String ,DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.db import Base


class Vehicle(Base):
    __tablename__ = "Vehicles"
    
    veh_id = Column(Integer, primary_key = True, index = True)
    veh_plate = Column(String(10), unique = True, nullable = False)
    veh_brand = Column(String(50), nullable = False)
    veh_model = Column(String(50), nullable = False)
    veh_year = Column(Integer, nullable = False)
    cli_id = Column(Integer,ForeignKey("Clients.cli_id"), nullable = False)
    ses_id = Column(Integer, ForeignKey("Sessions.ses_id"),nullable = False)    
    cli_date_mod = Column(DateTime, default = func.now(), onupdate = func.now())
    
    client = relationship("Client", back_populates = "vehicles")
    orders = relationship("Order", back_populates = "vehicle", cascade="all, delete-orphan")