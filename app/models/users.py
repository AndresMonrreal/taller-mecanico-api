from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base

class User(Base):
    __tablename__ = "users"

    usr_id = Column(Integer, primary_key=True, index=True)
    usr_username = Column(String(100), unique=True, nullable=False)
    usr_password = Column(String(255), nullable=False)
    usr_rol = Column(String(50), nullable=False, default="reception")
    ses_id = Column(Integer, ForeignKey("Sessions.ses_id"), nullable=True)