from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, deferred
from app.core.db import Base

class Service(Base):
    __tablename__ = "Service"

    __table_args__ = (
        CheckConstraint("srv_price_hour > 0", name="ck_servicio_precio"),
    )

    srv_id = Column(Integer, primary_key=True, index=True)
    srv_name = Column(String(100), unique=True, nullable=False)
    srv_price_hour = Column(Numeric(10, 2), nullable=False)
    srv_date_mod = Column(DateTime, default=func.now(), onupdate=func.now())
    ses_id = deferred(Column(Integer, nullable=True))

    service_orders = relationship("ServiceOrder", back_populates="service")
    
    