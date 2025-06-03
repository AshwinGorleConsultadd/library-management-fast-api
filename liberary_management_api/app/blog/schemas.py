from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

#schemas for user
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: Optional[str] = "user"
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
    role: str
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

#################
class User(BaseModel):
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
