from sqlalchemy import  Column,Integer,DateTime,String,Boolean
from src.utils.db import Base

class UserModel(Base):
    __tablename__ = "user_table"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100) , nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(255), nullable=True)
    email = Column(String(100), nullable=False, unique=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    google_id = Column(String(255), nullable=True, unique=True)
