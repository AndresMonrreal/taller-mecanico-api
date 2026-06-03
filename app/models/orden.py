from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, deferred
from app.core.db import Base


class Order(Base):
    """
    Modelo que representa una orden de trabajo en el taller.
    Agrupa servicios realizados a un vehículo y mantiene su estado de avance.
    """
    __tablename__ = "Orders"

    __table_args__ = (
        CheckConstraint("ord_status IN ('ABIERTA','EN_PROCESO','CERRADA')", name="ck_orden_estado"),  # Estados válidos
        Index("idx_ordenes_status_fecha", "ord_status", "ord_date"),  # Índice para consultas por estado y fecha
    )

    ord_id = Column(Integer, primary_key=True, index=True)        # ID único de la orden
    ord_date = Column(DateTime, default=func.now())               # Fecha de creación
    ord_status = Column(String(50), default="ABIERTA", nullable=False)  # Estado: ABIERTA | EN_PROCESO | CERRADA
    ord_urgency = Column(String(50), nullable=True)               # Nivel de urgencia (opcional)
    ord_notes = Column(String(500), nullable=True)                # Notas u observaciones
    ses_id = deferred(Column(Integer, nullable=True))             # ID de sesión (carga diferida)
    veh_id = Column(Integer, ForeignKey("Vehicles.veh_id"), nullable=False)  # FK al vehículo

    vehicle = relationship("Vehicle", back_populates="orders")
    services = relationship("ServiceOrder", back_populates="order")