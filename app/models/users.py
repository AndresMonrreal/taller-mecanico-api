from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base


class User(Base):
    """
    Modelo que representa a un usuario del sistema con credenciales y rol asignado.
    Se usa para autenticación y control de acceso.
    """
    __tablename__ = "users"

    usr_id = Column(Integer, primary_key=True, index=True)              # ID único del usuario
    usr_username = Column(String(100), unique=True, nullable=False)     # Nombre de usuario (único)
    usr_password = Column(String(255), nullable=False)                  # Hash bcrypt de la contraseña
    usr_rol = Column(String(50), nullable=False, default="reception")   # Rol asignado (admin, mecanico, recepcion, cliente)
