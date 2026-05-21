from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    usr_username: str
    usr_password: str
    usr_rol: Optional[str] = "recepcion"

class UserLogin(BaseModel):
    usr_username: str
    usr_password: str

class UserOut(BaseModel):
    usr_id: int
    usr_username: str
    usr_rol: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    rol: str
    usr_username: str

class PermisoRolOut(BaseModel):
    rol_nombre: str
    permiso_bitmask: int

    class Config:
        from_attributes = True