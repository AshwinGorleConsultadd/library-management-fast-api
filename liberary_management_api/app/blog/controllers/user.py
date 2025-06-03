
from sqlalchemy.orm import Session
from .. import models, schemas
from fastapi import HTTPException, status
from ..hashing import Hash


def create(request: schemas.User, db: Session):
    new_user = models.User(
        name=request.name, email=request.email, password=Hash.bcrypt(request.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def show(id: int, db: Session):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with the id {id} is not available")
    return user

def update_user(user, request: schemas.UserUpdate, db: Session):
    db_user = db.query(models.User).filter(models.User.email == user["email"]).first()
    if request.email:
        db_user.email = request.email
    if request.username:
        db_user.username = request.username
    if request.image:
        db_user.image = request.image
    if request.password:
        db_user.password = Hash.bcrypt(request.password)
    if request.name :
        db_user.name = request.name
    db.commit()
    return {"message": "User updated"}