from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class ServiceBase(BaseModel):
    """Schema base con los campos de un servicio del taller."""
    srv_name: str               # Nombre del servicio
    srv_price_hour: Decimal     # Precio por hora


class ServiceCreate(ServiceBase):
    """Schema para crear un nuevo servicio."""
    pass


class ServiceUpdate(BaseModel):
    """Schema para actualizar un servicio. Todos los campos son opcionales."""
    srv_name: Optional[str] = None
    srv_price_hour: Optional[Decimal] = None


class ServiceOut(ServiceBase):
    """Schema de respuesta con los datos del servicio, incluyendo su ID."""
    srv_id: int

    class Config:
        from_attributes = True        