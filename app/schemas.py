from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
#schemas for user
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    image: Optional[str] = None
    # is_varified: Optional[bool] = False

class UserUpdate(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    username: Optional[str]
    image: Optional[str]
    password: Optional[str]

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: Optional[str]
    image: Optional[str] = None
    is_varified: Optional[bool] = False

    class Config:
        orm_mode = True


#schemas for auth

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class VerifyRequest(BaseModel):
    email: EmailStr
    otp: str

class SignupResponse(BaseModel):
    message: str
    detail: str

class VerifyResponse(BaseModel):
    message: str
    detail: str
    access_token: str
    token_type: str = "bearer"

#schemas for books
class Book(BaseModel):
    title: str
    author: str
    isbn: str
    total_copies: Optional[int] = 0
    borrowed_copies: Optional[int] = 0
    available_copies: Optional[int] = 0

class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    total_copies: int

class BookResponse(BookBase):
    id: int
    available_copies: int
    borrowed_copies: int

    class Config:
        orm_mode = True

class BookUpdateRequest (BaseModel) :
    title: Optional[str]
    author: Optional[str]
    isbn: Optional[str]
    total_copies: Optional[int]
    borrowed_copies: Optional[int]
    available_copies: Optional[int]

class BorrowRequest(BaseModel):
    book_id: int

class BorrowResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    borrow_date: datetime
    return_date: datetime | None

    class Config:
        orm_mode = True

######
class User(BaseModel):
    id: int
    name:str
    email:str
    password:str

class Login(BaseModel):
    username: str
    password:str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
