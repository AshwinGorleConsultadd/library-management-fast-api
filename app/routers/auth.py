from urllib import request

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import database, schemas
from ..controllers import auth
from ..oauth2 import  get_current_user
from ..oauth2 import oauth2_scheme
router = APIRouter(tags=["Authentication"], prefix="/auth")

@router.post('/login')
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    return auth.login(request, db)

@router.post('/signup', response_model=schemas.SignupResponse)
def signup(request: schemas.UserCreate, db: Session = Depends(database.get_db)):
    print("auth-signup called")
    return auth.signup(request, db)

@router.post('/verify-email', response_model=schemas.VerifyResponse)
def verify_email(request: schemas.VerifyRequest, db: Session = Depends(database.get_db)):
    return auth.verify_email(request, db)

@router.post('/resend-otp', response_model=schemas.ResendOtpResponse)
def resend_otp(request: schemas.ResendOtpRequest, db: Session = Depends(database.get_db)):
    return auth.resend_otp(request, db)
@router.post("/change-password")
def change_password(request: schemas.ChangePasswordRequest, db: Session = Depends(database.get_db), user=Depends(get_current_user)):
    return auth.change_password(user, request, db)

@router.post("/refresh")
def refresh(request: schemas.TokenRefreshRequest):
    return auth.refresh_token(request)

@router.post("/logout")
def logout(user = Depends(get_current_user), db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)):
    return auth.logout(db,user,token)

@router.get("/me", response_model=schemas.UserResponse)
def me(user=Depends(get_current_user), db: Session = Depends(database.get_db)):
    return auth.get_me(user, db)

