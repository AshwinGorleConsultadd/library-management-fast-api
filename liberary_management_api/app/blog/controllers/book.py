from sqlalchemy.orm import Session
from .. import models, schemas
from datetime import datetime

# 1. Create a new book
def create_book(request: schemas.Book, db: Session):
    book = models.Book(
        title=request.title,
        author=request.author,
        isbn=request.isbn,
        total_copies=request.total_copies,
        available_copies=request.total_copies,
        borrowed_copies=0
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book

# 2. Get all books
def get_all_books(db: Session):
    return db.query(models.Book).all()

# 3. Get book by ID
def get_book(book_id: int, db: Session):
    return db.query(models.Book).filter(models.Book.id == book_id).first()

# 4. Update book
def update_book(book_id: int, request: schemas.BookUpdateRequest, db: Session):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        return None

    # Update fields if present
    if request.title is not None:
        book.title = request.title
    if request.author is not None:
        book.author = request.author
    if request.isbn is not None:
        book.isbn = request.isbn
    if request.total_copies is not None:
        diff = request.total_copies - book.total_copies
        book.total_copies = request.total_copies
        book.available_copies += diff
        # prevent available_copies from going negative
        if book.available_copies < 0:
            book.available_copies = 0

    db.commit()
    db.refresh(book)
    return book

# 5. Delete book
def delete_book(book_id: int, db: Session):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        return False

    db.delete(book)
    db.commit()
    return True

## borrow related controllers

def borrow_book(user: dict, request: schemas.BorrowRequest, db: Session):
    book = db.query(models.Book).filter(models.Book.id == request.book_id).first()
    if not book or book.available_copies <= 0:
        return None

    book.borrowed_copies += 1
    book.available_copies -= 1

    borrow = models.Borrow(
        user_id=user["id"],
        book_id=request.book_id
    )
    db.add(borrow)
    db.commit()
    db.refresh(borrow)
    return borrow

def return_book(borrow_id: int, user: dict, db: Session):
    borrow = db.query(models.Borrow).filter(models.Borrow.id == borrow_id).first()
    if not borrow or borrow.user_id != user["id"] or borrow.return_date is not None:
        return None

    borrow.return_date = datetime.utcnow()

    book = db.query(models.Book).filter(models.Book.id == borrow.book_id).first()
    book.available_copies += 1
    book.borrowed_copies -= 1

    db.commit()
    db.refresh(borrow)
    return borrow

def get_borrow_history(book_id: int, db: Session):
    return db.query(models.Borrow).filter(models.Borrow.book_id == book_id).all()
