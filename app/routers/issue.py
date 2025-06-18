from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..schemas import IssueCreate, ReturnBook, IssueResponse, IssuedBookResponse
from ..controllers import issue
from ..database import get_db
from typing import List
router = APIRouter(prefix="/issue", tags=["Issue"])

@router.post("/", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
def issue_book(data: IssueCreate, db: Session = Depends(get_db)):
    return issue.issue_book(db, data)

@router.put("/return/{issue_id}", response_model=IssueResponse)
def return_book(issue_id: int, db: Session = Depends(get_db)):
    return issue.return_book(db, issue_id)

@router.get("/", response_model=List[IssuedBookResponse])
def get_all_issued_books(db: Session = Depends(get_db)):
    return issue.get_all_issued_books(db)

