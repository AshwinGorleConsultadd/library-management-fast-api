from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.dialects.mysql import DATETIME

from .database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)
    role = Column(String, default='user')
    is_varified = Column(Boolean, default=False)
    otp = Column(String, default="")
    otp_expires = Column(DATETIME, default=None)