from sqlalchemy import Column, Integer, String, DateTime ,ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.db import Base

class Client(Base):
    __tablename__ ="Clients"
    
    cli_id = Column(Integer, primary_key = True, index =True)
    cli_name = Column(String(100), nullable = False)
    cli_phone = Column(String(10), unique = True, nullable = False)
    cli_email = Column(String(100), unique = True, nullable = False)
    cli_date_mod = Column(DateTime, default = func.now(), onupdate = func.now())
    ses_id = Column(Integer, ForeignKey("Sessions.ses_id"), nullable=True)    
    session = relationship("Session")
    vehicles = relationship("Vehicle", back_populates = "client",cascade="all, delete-orphan")
    

    