from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ServiceOrderBase(BaseModel):
    """Schema base para asociar un servicio a una orden (detalle)."""
    srv_id: int             # ID del servicio
    ords_hours: Decimal     # Horas trabajadas


class ServiceOrderOut(ServiceOrderBase):
    """Schema de respuesta para un detalle de servicio en una orden."""
    srv_ord_id: int                         # ID del detalle
    ords_total: Optional[Decimal] = None    # Costo total calculado

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    """Schema base con los campos comunes de una orden de trabajo."""
    veh_id: int                      # ID del vehículo
    ord_status: Optional[str] = "ABIERTA"   # Estado inicial
    ord_notes: Optional[str] = None         # Notas opcionales


class OrderCreate(OrderBase):
    """Schema para crear una nueva orden, incluyendo lista de servicios."""
    services: Optional[list[ServiceOrderBase]] = []


class OrderUpdate(BaseModel):
    """Schema para actualizar una orden existente. Todos los campos son opcionales."""
    ord_status: Optional[str] = None
    ord_notes: Optional[str] = None
    ord_urgency: Optional[str] = None
    veh_id: Optional[int] = None


class OrderOut(OrderBase):
    """Schema de respuesta con datos completos de la orden y sus servicios."""
    ord_id: int
    ord_date: Optional[datetime] = None
    ord_urgency: Optional[str] = None
    services: Optional[list[ServiceOrderOut]] = []

    class Config:
        from_attributes = True    