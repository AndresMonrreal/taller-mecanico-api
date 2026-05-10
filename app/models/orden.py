from sqlalchemy import Column, Integer, String, DateTime ,ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.db import Base

class Order(Base):
    __tablename__ = "Orders"
    
    ord_id = Column(Integer, primary_key = True, index = True)
    ord_date = Column(DateTime, default = func.now())
    ord_status = Column(String(50), default = "open", nullable = False)
    ord_urgency = Column(String(50), nullable=True)     
    ord_notes = Column(String(500), nullable=True)
    ses_id = Column(Integer, ForeignKey("Sessions.ses_id"), nullable=True)
    veh_id = Column(Integer, ForeignKey("Vehicles.veh_id"), nullable = False)
    
    vehicle = relationship("Vehicle", back_populates = "orders")
    services = relationship("ServiceOrder", back_populates = "order")