from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.dialects.mysql import DATETIME
from datetime import datetime
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
    borrows = relationship("Borrow", back_populates="user")

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    isbn = Column(String, nullable=True)

    total_copies = Column(Integer, default=1)
    borrowed_copies = Column(Integer, default=0)
    available_copies = Column(Integer, default=1)

    borrows = relationship("Borrow", back_populates="book")

class Borrow(Base):
    __tablename__ = "borrows"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))

    borrow_date = Column(DateTime, default=datetime.utcnow)
    return_date = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="borrows")
    book = relationship("Book", back_populates="borrows")

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False)
    blacklisted_at = Column(DateTime, default=datetime.utcnow)