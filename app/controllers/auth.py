from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from .. import models, token, schemas
from ..hashing import Hash
from datetime import datetime, timedelta
from ..models import BlacklistedToken

FIXED_OTP = "1234"
OTP_VALIDITY_MINUTES = 10

def login(request: OAuth2PasswordRequestForm, db: Session):
    user = db.query(models.User).filter(models.User.email == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid Credentials")

    if not user.is_varified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Please verify your email before logging in.")

    if not Hash.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Incorrect password")

    access_token = token.create_access_token(
        data={"sub": user.email, "role": user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}


def signup(request: schemas.UserCreate, db: Session):
    existing = db.query(models.User).filter(models.User.email == request.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email already registered")

    # 1. Creatinf the new user
    new_user = models.User(
        name=request.name,
        email=request.email,
        password=Hash.bcrypt(request.password),
        role=request.role,
        is_varified=False,
        otp=FIXED_OTP,
        otp_expires=datetime.utcnow() + timedelta(minutes=OTP_VALIDITY_MINUTES)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)


    return {
        "message": "Signup successful",
        "detail": "An OTP has been sent to your email. Please verify your account."
    }

def change_password(user, request: schemas.ChangePasswordRequest, db: Session):
    db_user = db.query(models.User).filter(models.User.email == user["email"]).first()
    if not Hash.verify(db_user.password, request.old_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    db_user.password = Hash.bcrypt(request.new_password)
    db.commit()
    return {"message": "Password updated successfully"}


def refresh_token(request: schemas.TokenRefreshRequest):
    try:
        payload = jwt.decode(request.refresh_token, "secret", algorithms=["HS256"])
        email = payload.get("sub")
        role = payload.get("role")
        new_token = token.create_access_token(data={"sub": email, "role": role})
        return {"access_token": new_token, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

def logout(db, user, token):
    blacklisted = BlacklistedToken(token=token)
    db.add(blacklisted)
    db.commit()
    return {"message": "Logout successful"}

def get_me(user, db):
    return  db.query(models.User).filter(models.User.email == user["email"]).first()

def verify_email(request: schemas.VerifyRequest, db: Session):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_varified:
        access_token = token.create_access_token(data={"sub": user.email, "role": user.role})
        return {
            "message": "Already verified",
            "detail": "your account is already verified.",
            "access_token": access_token,
            "token_type": "bearer"
        }

    if request.otp != user.otp or datetime.utcnow() > user.otp_expires:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    user.is_varified = True
    user.otp = ""
    user.otp_expires = None
    db.commit()
    db.refresh(user)

    access_token = token.create_access_token(data={"sub": user.email, "role": user.role})
    return {
        "message": "Email verified successfully",
        "detail": "You can now log in.",
        "access_token": access_token,
        "token_type": "bearer"
    }
