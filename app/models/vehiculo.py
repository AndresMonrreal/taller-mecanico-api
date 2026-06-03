from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, deferred
from app.core.db import Base


class Vehicle(Base):
    """
    Modelo que representa un vehículo asociado a un cliente.
    Cada vehículo puede tener múltiples órdenes de trabajo.
    """
    __tablename__ = "Vehicles"

    __table_args__ = (
        CheckConstraint("veh_year > 1900", name="ck_vehiculo_anio"),  # El año debe ser mayor a 1900
    )

    veh_id = Column(Integer, primary_key=True, index=True)        # ID único del vehículo
    veh_plate = Column(String(10), unique=True, nullable=False)   # Placa/Número de matrícula (único)
    veh_brand = Column(String(50), nullable=False)                # Marca del vehículo (ej: Toyota, Ford)
    veh_model = Column(String(50), nullable=False)                # Modelo del vehículo (ej: Corolla, F-150)
    veh_year = Column(Integer, nullable=False)                    # Año de fabricación
    cli_id = Column(Integer, ForeignKey("Clients.cli_id"), nullable=False)  # FK al cliente propietario
    ses_id = deferred(Column(Integer, nullable=True))             # ID de sesión (carga diferida)
    veh_date_mod = Column(DateTime, default=func.now(), onupdate=func.now())  # Fecha de última modificación

    client = relationship("Client", back_populates="vehicles")
    orders = relationship("Order", back_populates="vehicle", cascade="all, delete-orphan")