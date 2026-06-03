from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.db import Base


class Session(Base):
    """
    Modelo que registra las sesiones de inicio de sesión de los usuarios.
    Lleva un historial de quién y cuándo accedió al sistema.
    """
    __tablename__ = "Sessions"

    ses_id = Column(Integer, primary_key=True, index=True)        # ID único de la sesión
    ses_usuario = Column(String(100), nullable=False)             # Nombre de usuario que inició sesión
    ses_fecha = Column(DateTime(timezone=True), server_default=func.now())  # Fecha y hora del inicio de sesión
    
    
