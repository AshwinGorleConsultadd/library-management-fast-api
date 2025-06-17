from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app import database, schemas
from app.controllers import member
from ..core.rbac import role_required

router = APIRouter(
    prefix="/members",
    tags=["Members"],
    dependencies=[Depends(role_required(["admin"]))]
)

# Get all members
@router.get("/", response_model=List[schemas.UserResponse])
def get_members(db: Session = Depends(database.get_db)):
    return member.get_all_members(db)

# Add new member
@router.post("/", response_model=schemas.UserResponse)
def add_member(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    return member.create_member(user, db)

# Update member
@router.put("/{member_id}", response_model=schemas.UserResponse)
def update_member(member_id: int, user: schemas.UserUpdate, db: Session = Depends(database.get_db)):
    return member.update_member(member_id, user, db)

# Delete member
@router.delete("/{member_id}")
def delete_member(member_id: int, db: Session = Depends(database.get_db)):
    return member.delete_member(member_id, db)
