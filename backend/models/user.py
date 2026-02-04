from sqlalchemy import Column, Integer, String, Text, DateTime
from db.db import Base
from datetime import datetime

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default='hr')  # 'hr' or 'admin'
    created_at = Column(DateTime, default=datetime.utcnow)