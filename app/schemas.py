from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
#schemas for user
class UserCreate(BaseModel):
    name: str
    email: str
    password: Optional[str] = None
    image: Optional[str] = None
    # is_varified: Optional[bool] = False
class SignupRequest(BaseModel) :
    name: str
    email: str
    password: str
    confirm_password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    image: Optional[str] = None
    password: Optional[str] = None

class UserResponse(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
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
    email: str
    otp: str

class SignupResponse(BaseModel):
    message: str
    detail: str
    email : str

class ResendOtpResponse(BaseModel):
    message: str
    email: str

class ResendOtpRequest(BaseModel):
    email: str

class VerifyResponse(BaseModel):
    message: str
    detail: str
    access_token: str
    token_type: str = "bearer"

#schemas for books
class Book(BaseModel):
    id : int
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

class CreateBookRequest(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    total_copies: Optional[int] = None
    borrowed_copies: Optional[int] = None
    available_copies: Optional[int] = None

class BookUpdateRequest(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    total_copies: Optional[int] = None
    borrowed_copies: Optional[int] = None
    available_copies: Optional[int] = None

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

class IssueCreate(BaseModel):
    user_id: int
    book_id: int

class ReturnBook(BaseModel):
    issue_id: int

class IssueResponse(BaseModel):
    id: int
    user: UserResponse
    book: BookResponse
    issue_date: datetime
    return_date: datetime | None

    class Config:
        orm_mode = True

class IssuedBookResponse(BaseModel):
    id: int
    user: UserResponse
    book: BookResponse
    issue_date: datetime
    return_date: datetime | None

    class Config:
        orm_mode = True