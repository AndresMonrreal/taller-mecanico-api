from sqlalchemy import Column, Integer, Numeric, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship, deferred
from app.core.db import Base

class ServiceOrder(Base):
    __tablename__ = "ServiceOrders"

    __table_args__ = (
        UniqueConstraint("ord_id", "srv_id", name="uq_ord_servicio"),
        CheckConstraint("ords_hours > 0", name="ck_ords_horas_positivas"),
    )

    srv_ord_id = Column(Integer, primary_key=True, index=True)
    ord_id = Column(Integer, ForeignKey("Orders.ord_id"), nullable=False)
    srv_id = Column(Integer, ForeignKey("Service.srv_id"), nullable=False)
    ords_hours = Column(Numeric(5, 2), nullable=False)
    ords_total = Column(Numeric(10, 2), nullable=True)
    ses_id = deferred(Column(Integer, nullable=True))

    order = relationship("Order", back_populates="services")
    service = relationship("Service", back_populates="service_orders")
    