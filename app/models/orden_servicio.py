from sqlalchemy import Column, Integer, Numeric, String, DateTime ,ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.db import Base

class ServiceOrder(Base):
    __tablename__ = "ServiceOrders"
    
    srv_ord_id = Column(Integer, primary_key = True, index = True)
    ord_id = Column(Integer, ForeignKey("Orders.ord_id"), nullable = False)
    srv_id = Column(Integer, ForeignKey("Service.srv_id"), nullable = False)
    ords_hours = Column(Numeric(5, 2), nullable=False)
    ords_total = Column(Numeric(10, 2), nullable=True)
    ses_id = Column(Integer, ForeignKey("sesiones.ses_id"), nullable=True)

    order = relationship("Order", back_populates="services")
    service = relationship("Service", back_populates="service_orders")
    