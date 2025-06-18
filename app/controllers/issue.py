from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy.orm import joinedload
from ..models import IssuedBook
from ..models import Book
from ..models import User
from ..schemas import IssueCreate

def issue_book(db: Session, issue_data: IssueCreate):
    # check if book exists
    book = db.query(Book).filter(Book.id == issue_data.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # check availability
    if book.available_copies < 1:
        raise HTTPException(status_code=400, detail="No available copies")

    # check if member exists
    member = db.query(User).filter(User.id == issue_data.user_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="User not found")

    # create issue entry
    issue = IssuedBook(
        user_id=issue_data.user_id,
        book_id=issue_data.book_id
    )

    book.available_copies -= 1

    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue

def return_book(db: Session, issue_id: int):
    issue = (
        db.query(IssuedBook)
        .options(
            joinedload(IssuedBook.user),
            joinedload(IssuedBook.book)
        )
        .filter(IssuedBook.id == issue_id)
        .first()
    )

    if not issue:
        raise HTTPException(status_code=404, detail="Issue record not found")
    if issue.return_date is not None:
        raise HTTPException(status_code=400, detail="Book already returned")

    issue.return_date = datetime.utcnow()

    issue.book.available_copies += 1  # already loaded via joinedload

    db.commit()
    db.refresh(issue)
    return issue


def get_all_issued_books(db: Session):
    issued_books = (
        db.query(IssuedBook)
        .options(
            joinedload(IssuedBook.user),  # eager load User
            joinedload(IssuedBook.book)   # eager load Book
        )
        .all()
    )
    return issued_books
