from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class ClientBase(BaseModel):
    cli_name: str
    cli_phone: str
    cli_email: EmailStr
    
class ClientCreate(ClientBase):
    pass

class ClientUpdate(ClientBase):
    cli_name: Optional[str] = None
    cli_phone: Optional[str] = None
    cli_email: Optional[EmailStr] = None
    
class ClientOut(ClientBase):
    cli_id: int
    cli_date_mod: Optional[datetime] = None

    class Config:
        from_attributes = True        
    