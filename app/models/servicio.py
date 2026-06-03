from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, deferred
from app.core.db import Base


class Service(Base):
    """
    Modelo que representa un servicio ofrecido por el taller.
    Ej: cambio de aceite, alineación, diagnóstico, etc.
    """
    __tablename__ = "Service"

    __table_args__ = (
        CheckConstraint("srv_price_hour > 0", name="ck_servicio_precio"),  # El precio por hora debe ser positivo
    )

    srv_id = Column(Integer, primary_key=True, index=True)          # ID único del servicio
    srv_name = Column(String(100), unique=True, nullable=False)     # Nombre del servicio (único)
    srv_price_hour = Column(Numeric(10, 2), nullable=False)         # Precio por hora del servicio
    srv_date_mod = Column(DateTime, default=func.now(), onupdate=func.now())  # Fecha de última modificación
    ses_id = deferred(Column(Integer, nullable=True))               # ID de sesión (carga diferida)

    service_orders = relationship("ServiceOrder", back_populates="service")
    
    