from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VehicleBase(BaseModel):
    """Schema base con los campos de un vehículo."""
    veh_plate: str    # Placa o matrícula
    veh_brand: str    # Marca
    veh_model: str    # Modelo
    veh_year: int     # Año de fabricación
    cli_id: int       # ID del cliente propietario


class VehicleCreate(VehicleBase):
    """Schema para registrar un nuevo vehículo."""
    pass


class VehicleUpdate(BaseModel):
    """Schema para actualizar un vehículo. Todos los campos son opcionales."""
    veh_plate: Optional[str] = None
    veh_brand: Optional[str] = None
    veh_model: Optional[str] = None
    veh_year: Optional[int] = None
    cli_id: Optional[int] = None


class VehicleOut(VehicleBase):
    """Schema de respuesta con los datos del vehículo, incluyendo su ID."""
    veh_id: int

    class Config:
        from_attributes = True        