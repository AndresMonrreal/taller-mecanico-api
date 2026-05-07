from sqlalchemy import Column, Integer, String , DateTime
from sqlalchemy.sql import func
from app.core.db import Base

class Session(Base):
    __tablename__ = "Sessions"
    
    ses_id = Column(Integer, primary_key = True, index = True)
    ses_usuario = Column(String(100), nullable = False)
    ses_fecha = Column(DateTime(timezone = True), server_default = func.now())
    
    
