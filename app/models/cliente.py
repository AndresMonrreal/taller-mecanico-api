from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, deferred
from app.core.db import Base


class Client(Base):
    """
    Modelo que representa a un cliente del taller.
    Almacena datos de contacto y está asociado a uno o más vehículos.
    """
    __tablename__ = "Clients"

    cli_id = Column(Integer, primary_key=True, index=True)       # ID único del cliente
    cli_name = Column(String(100), nullable=False)               # Nombre completo del cliente
    cli_phone = Column(String(10), unique=True, nullable=False)  # Teléfono (único)
    cli_email = Column(String(100), unique=True, nullable=False) # Correo electrónico (único)
    cli_date_mod = Column(DateTime, default=func.now(), onupdate=func.now())  # Fecha de última modificación
    ses_id = deferred(Column(Integer, nullable=True))            # ID de sesión (carga diferida)
    vehicles = relationship("Vehicle", back_populates="client", cascade="all, delete-orphan")  # Vehículos del cliente
    

    