from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VehicleBase(BaseModel):
    veh_plate: str
    veh_brand: str
    veh_model: str
    veh_year: int
    cli_id: int
    
class VehicleCreate(VehicleBase):
    pass

class VehicleUpdate(BaseModel):
    veh_plate: Optional[str] = None
    veh_brand: Optional[str] = None
    veh_model: Optional[str] = None
    veh_year: Optional[int] = None
    cli_id: Optional[int] = None
    
class VehicleOut(VehicleBase):
    veh_id: int

    class Config:
        from_attributes = True        