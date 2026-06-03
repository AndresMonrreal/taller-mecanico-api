from sqlalchemy import Column, Integer, Numeric, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship, deferred
from app.core.db import Base


class ServiceOrder(Base):
    """
    Modelo asociativo (tabla pivote) entre órdenes de trabajo y servicios.
    Cada registro vincula un servicio a una orden con horas y costo calculado.
    """
    __tablename__ = "ServiceOrders"

    __table_args__ = (
        UniqueConstraint("ord_id", "srv_id", name="uq_ord_servicio"),     # Evita duplicar el mismo servicio en una orden
        CheckConstraint("ords_hours > 0", name="ck_ords_horas_positivas"), # Horas trabajadas deben ser positivas
    )

    srv_ord_id = Column(Integer, primary_key=True, index=True)             # ID único del detalle
    ord_id = Column(Integer, ForeignKey("Orders.ord_id"), nullable=False)  # FK a la orden de trabajo
    srv_id = Column(Integer, ForeignKey("Service.srv_id"), nullable=False) # FK al servicio
    ords_hours = Column(Numeric(5, 2), nullable=False)                     # Horas trabajadas en este servicio
    ords_total = Column(Numeric(10, 2), nullable=True)                     # Costo total calculado (horas * precio)
    ses_id = deferred(Column(Integer, nullable=True))                      # ID de sesión (carga diferida)

    order = relationship("Order", back_populates="services")
    service = relationship("Service", back_populates="service_orders")
    