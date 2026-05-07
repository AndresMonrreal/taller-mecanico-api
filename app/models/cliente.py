from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.db import Base

class Client(Base):
    __tablename__ ="Clients"
    
    cli_Id = Column(Integer, primary_key = True, index =True)
    cli_nombre = Column(String(100), nullable = False)