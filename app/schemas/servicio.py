from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class ServiceBase(BaseModel):
    srv_name: str
    srv_price_hour: Decimal
    
class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    srv_name: Optional[str] = None
    srv_price_hour: Optional[Decimal] = None
    
class ServiceOut(ServiceBase):
    srv_id: int

    class Config:
        from_attributes = True        