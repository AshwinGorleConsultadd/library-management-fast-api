# FastAPI Library Management System – Complete Flow (Ashwin)

This document explains the entire FastAPI-based Library Management System with **step-by-step flow** and **clear definitions** for each component. Ideal for beginners and developers transitioning from Django or Node.js.

---

## 🛠️ 1. Project Setup

### ➤ What is this?
This step sets up your Python environment, creates the FastAPI app structure, and installs dependencies.

### ✅ Commands:
```bash
mkdir library_fastapi
cd library_fastapi
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy pydantic alembic python-jose[cryptography] passlib[bcrypt] python-dotenv
```

---

## 2. Project Structure

### ➤ Why structure matters?
A clean project structure keeps your code organized and scalable.

### ✅ Example Structure:
```
library_fastapi/
│
├── app/
│   ├── main.py
│   ├── models/
│   │   └── book.py
│   ├── schemas/
│   │   └── book.py
│   ├── controllers/
│   │   └── bookcontroller.py
│   ├── routers/
│   │   └── bookroute.py
│   ├── database.py
│   └── auth/
│       ├── hashing.py
│       ├── jwt.py
│       └── authcontroller.py
│
├── .env
└── requirements.txt
```

---

## 3. `main.py` – App Entry Point

### ➤ What does this do?
This file runs your FastAPI server and includes routing setup.

```python
from fastapi import FastAPI
from app.routers import bookroute

app = FastAPI()

app.include_router(bookroute.router, prefix="/api/books", tags=["Books"])
```

---

## 4. Routing

### ➤ What is Routing?
Routing maps incoming HTTP requests to specific functions (views).

### ✅ In `bookroute.py`
```python
from fastapi import APIRouter
from app.controllers import bookcontroller

router = APIRouter()

router.post("/", response_model=schemas.ShowBook)(bookcontroller.create_book)
router.get("/", response_model=list[schemas.ShowBook])(bookcontroller.get_all_books)
router.get("/{book_id}", response_model=schemas.ShowBook)(bookcontroller.get_book_by_id)
router.put("/{book_id}")(bookcontroller.update_book)
router.delete("/{book_id}")(bookcontroller.delete_book)
```

---

## 5. Models (SQLAlchemy ORM)

### ➤ What is a Model?
It defines the structure of your database table and represents data objects.

### ✅ In `models/book.py`
```python
from sqlalchemy import Column, Integer, String
from app.database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    total_copies = Column(Integer)
    borrowed_copies = Column(Integer, default=0)

    def available_copies(self):
        return self.total_copies - self.borrowed_copies
```

---

## 6. Schemas (Pydantic)

### ➤ What is a Schema?
Schemas define the shape of request and response data using Pydantic models.

### ✅ In `schemas/book.py`
```python
from pydantic import BaseModel

class BookBase(BaseModel):
    title: str
    author: str
    total_copies: int
    borrowed_copies: int = 0

class ShowBook(BookBase):
    id: int
    class Config:
        orm_mode = True
```

---

## 7. Controllers (Business Logic)

### ➤ What is a Controller?
It handles the business logic between request input and database actions.

### ✅ In `controllers/bookcontroller.py`
```python
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

def create_book(request: schemas.BookBase, db: Session = Depends(get_db)):
    new_book = models.Book(**request.dict())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

def get_all_books(db: Session = Depends(get_db)):
    return db.query(models.Book).all()

def get_book_by_id(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

def update_book(book_id: int, request: schemas.BookBase, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in request.dict().items():
        setattr(book, key, value)
    db.commit()
    return book

def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return {"detail": "Deleted"}
```

---

## 8. Database Config

### ➤ What is this?
It sets up your SQLAlchemy DB connection and session.

### ✅ In `database.py`
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./library.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 9. JWT Authentication

### ➤ What is JWT?
JWT (JSON Web Token) is used for secure stateless authentication.

### ✅ Basic Auth Flow:
- User signs up → receives JWT token
- Token is sent in `Authorization: Bearer <token>` for protected routes

### ✅ Example: Verify Token
```python
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from datetime import datetime

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

---

##  10. Role-Based Access Control (RBAC)

### ➤ What is RBAC?
Restricts access to APIs based on user roles like `admin`, `user`, etc.

### ✅ Sample Role Check
```python
def is_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins allowed")
```

---

## 11. Borrow and Return Book

### ✅ In `controllers/bookcontroller.py`
```python
def borrow_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book or book.available_copies() <= 0:
        raise HTTPException(status_code=400, detail="No available copies")
    book.borrowed_copies += 1
    db.commit()
    return {"message": "Book borrowed successfully"}

def return_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book or book.borrowed_copies <= 0:
        raise HTTPException(status_code=400, detail="No borrowed copies to return")
    book.borrowed_copies -= 1
    db.commit()
    return {"message": "Book returned successfully"}
```

---

## 12. Full Flow Summary

### ➤ What happens on a request?
```
Client → Router (APIRouter) → Controller → Schema ↔ Model → DB → Response
```

FastAPI handles requests in a clean async-first, dependency-injected way.

---

## ✅ 13. Run the Server

### ✅ Command:
```bash
uvicorn app.main:app --reload
```

---

## Sample POST Request (Borrow Book)
```bash
POST /api/books/1/borrow

Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Book borrowed successfully"
}
```

---

## ✅ Final Notes
- Use `alembic` for migrations (optional).
- `.env` for sensitive data like `SECRET_KEY`.
- Use `pytest` and `TestClient` for testing.
