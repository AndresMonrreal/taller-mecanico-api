from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class ClientBase(BaseModel):
    """Schema base con los campos comunes de un cliente."""
    cli_name: str          # Nombre completo del cliente
    cli_phone: str         # Número de teléfono
    cli_email: EmailStr    # Correo electrónico


class ClientCreate(ClientBase):
    """Schema para la creación de un nuevo cliente (hereda todos los campos de ClientBase)."""
    pass


class ClientUpdate(BaseModel):
    """Schema para actualizar un cliente existente. Todos los campos son opcionales."""
    cli_name: Optional[str] = None
    cli_phone: Optional[str] = None
    cli_email: Optional[EmailStr] = None


class ClientOut(ClientBase):
    """Schema de respuesta con los datos completos del cliente, incluyendo ID y fechas."""
    cli_id: int
    cli_date_mod: Optional[datetime] = None

    class Config:
        from_attributes = True        
    