from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database
# from app.auth.role_check import role_required
# from ..core.rbac import role_required
# from typing import List


# Get all members (users)
def get_all_members(db: Session):
    return db.query(models.User).all()


# Create a new member
def create_member(user: schemas.UserCreate, db: Session):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = models.User(
        email=user.email,
        name=user.name,
        password=user.password,  # Make sure password is hashed in real use case
        role="member"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# Update a member
def update_member(member_id: int, user: schemas.UserUpdate, db: Session):
    member = db.query(models.User).filter(models.User.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="User not found")

    if user.name is not None:
        member.name = user.name
    if user.email is not None:
        member.email = user.email
    if user.password is not None:
        member.password = user.password  # Again, hash this in real-world apps

    db.commit()
    db.refresh(member)
    return member


# Delete a member
def delete_member(member_id: int, db: Session):
    member = db.query(models.User).filter(models.User.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(member)
    db.commit()
    return {"detail": "Member deleted"}
