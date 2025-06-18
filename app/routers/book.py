from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, schemas
from ..controllers import book
from ..core.rbac import role_required  # adjust path if needed
from ..oauth2 import get_current_user
router = APIRouter(prefix="/books", tags=["Books"])

@router.get("/", response_model=list[schemas.Book])
def get_all_books(db: Session = Depends(database.get_db)):
    return book.get_all_books(db)

@router.get("/{book_id}", response_model=schemas.Book)
def get_book_by_id(book_id: int, db: Session = Depends(database.get_db)):
    fetched_book = book.get_book(book_id, db)
    if not fetched_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return fetched_book

@router.post("/", response_model=schemas.Book)
def create_book(
    request: schemas.CreateBookRequest,
    db: Session = Depends(database.get_db),
    user=Depends(role_required(["admin"]))
):
    return book.create_book(request, db)

@router.put("/{book_id}", response_model=schemas.Book)
def update_book(
    book_id: int,
    request: schemas.BookUpdateRequest,
    db: Session = Depends(database.get_db),
    user=Depends(role_required(["admin"]))
):
    return book.update_book(book_id, request, db)

@router.delete("/{book_id}")
def delete_book(
    book_id: int,
    db: Session = Depends(database.get_db),
    user=Depends(role_required(["admin"]))
):
    book.delete_book(book_id, db)

# Borrow related routes
@router.post("/borrow", response_model=schemas.BorrowResponse)
def borrow(
    request: schemas.BorrowRequest,
    db: Session = Depends(database.get_db),
    user=Depends(get_current_user)
):
    return book.borrow_book(user, request, db)

@router.put("/return/{borrow_id}", response_model=schemas.BorrowResponse)
def return_book(
    borrow_id: int,
    db: Session = Depends(database.get_db),
    user=Depends(get_current_user)
):
    return book.return_book(borrow_id, db, user)

@router.get("/history/{book_id}", response_model=list[schemas.BorrowResponse])
def borrow_history(book_id: int, db: Session = Depends(database.get_db)):
    return book.get_borrow_history(book_id, db)