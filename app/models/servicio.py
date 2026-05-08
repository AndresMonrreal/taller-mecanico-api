from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.db import Base

class Service(Base):
    __tablename__ = "Service"
    srv_id = Column(Integer, primary_key = True, index = True)
    srv_name = Column(String(100), unique = True,nullable = False)
    srv_precio = Column(Numeric(10, 2), nullable = False)
    ses_id = Column(Integer, ForeignKey("sessions.ses_id"), nullable = True)
    srv_date_mod = Column(DateTime, default = func.now(), onupdate = func.now())
    
    
service_orders = relationship("ServiceOrder", back_populates = "service")
    
    