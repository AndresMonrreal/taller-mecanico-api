from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ServiceOrderBase(BaseModel):
    srv_id: int
    ords_hours: Decimal

class ServiceOrderOut(ServiceOrderBase):   
    ords_id: int
    ords_total: Optional[Decimal] = None
    
    class Config:
        from_attributes = True
        
class OrderBase(BaseModel):
    veh_id: int
    ord_status: Optional[str] = "Open" 
    ord_notes: Optional[str] = None
    
class OrderCreate(OrderBase):
    services: Optional[list[ServiceOrderBase]] = []
    
    
class OrderUpdate(BaseModel):
    ord_status: Optional[str] = None
    ord_notes: Optional[str] = None
    ord_urgency: Optional[str] = None
    
class OrderOut(OrderBase):
    ord_id: int
    ord_date: Optional[datetime] = None
    ord_urgency: Optional[str] = None
    services: Optional[list[ServiceOrderOut]] = []
    
    class Config:
        from_attributes = True    