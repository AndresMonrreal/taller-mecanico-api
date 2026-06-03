from sqlalchemy import Column, Integer, String
from app.core.db import Base


class PermisoRol(Base):
    """
    Modelo que almacena los roles y sus permisos asociados (bitmask) en la base de datos Oracle.
    Permite definir roles personalizados con permisos granulares.
    """
    __tablename__ = "permisos_rol"
    rol_id = Column(Integer, primary_key=True)               # ID único del rol
    rol_nombre = Column(String(50), unique=True, nullable=False)  # Nombre del rol (único)
    permiso_bitmask = Column(Integer, nullable=False)        # Máscara binaria de permisos del rol
