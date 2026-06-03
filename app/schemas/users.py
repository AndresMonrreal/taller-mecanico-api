from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    """Schema para el registro de un nuevo usuario."""
    usr_username: str                     # Nombre de usuario
    usr_password: str                     # Contraseña en texto plano
    usr_rol: Optional[str] = "recepcion"  # Rol asignado (default: recepcion)


class UserLogin(BaseModel):
    """Schema para el inicio de sesión (login)."""
    usr_username: str   # Nombre de usuario
    usr_password: str   # Contraseña


class UserOut(BaseModel):
    """Schema de respuesta con datos públicos del usuario (sin contraseña)."""
    usr_id: int
    usr_username: str
    usr_rol: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema de respuesta con el token JWT y datos del usuario autenticado."""
    access_token: str   # Token JWT
    token_type: str     # Tipo de token (ej: bearer)
    rol: str            # Rol del usuario
    usr_username: str   # Nombre de usuario


class PermisoRolOut(BaseModel):
    """Schema de respuesta con la información de un rol y su bitmask de permisos."""
    rol_nombre: str       # Nombre del rol
    permiso_bitmask: int  # Máscara binaria de permisos

    class Config:
        from_attributes = True