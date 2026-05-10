from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ServiceOrderBase(BaseModel):
    srv_id: int
    ords_hours: Decimal

class ServiceOrderOut(ServiceOrderBase):   
    srv_ord_id: int
    ords_total: Optional[Decimal] = None
    
    class Config:
        from_attributes = True
        
class OrderBase(BaseModel):
    veh_id: int
    ord_status: Optional[str] = "ABIERTA" 
    ord_notes: Optional[str] = None
    
class OrderCreate(OrderBase):
    services: Optional[list[ServiceOrderBase]] = []
    
    
class OrderUpdate(BaseModel):
    ord_status: Optional[str] = None
    ord_notes: Optional[str] = None
    ord_urgency: Optional[str] = None
    veh_id: Optional[int] = None # Add this if you allow changing the vehicle
    
class OrderOut(OrderBase):
    ord_id: int
    ord_date: Optional[datetime] = None
    ord_urgency: Optional[str] = None
    services: Optional[list[ServiceOrderOut]] = []
    
    class Config:
        from_attributes = True    