from .. import database, schemas
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from ..controllers import user
from ..oauth2 import get_current_user
router = APIRouter(
    prefix="/user",
    tags=['Users']
)

get_db = database.get_db


# @router.post('/', response_model=schemas.ShowUser)
# def create_user(request: schemas.User, db: Session = Depends(get_db)):
#     return user.create(request, db)


@router.get('/{id}', response_model=schemas.UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    return user.show(id, db)

@router.put("/")
def update_user(request: schemas.UserUpdate, db: Session = Depends(database.get_db), user=Depends(get_current_user)):
    return user.update_user(user, request, db)