from sqlalchemy import Column, Integer, String
from app.core.db import Base

class PermisoRol(Base):
    __tablename__ = "permisos_rol"
    rol_id = Column(Integer, primary_key=True)
    rol_nombre = Column(String(50), unique=True, nullable=False)
    permiso_bitmask = Column(Integer, nullable=False)
