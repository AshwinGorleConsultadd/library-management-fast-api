import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

from app.database import Base, get_db
from app.main import app
from app.core.init_admin import create_admin
from dotenv import load_dotenv

load_dotenv()

# DB setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_db.sqlite3"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ADMIN_EMAIL = os.getenv("ADMIN_USERNAME", "admin")
# ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

@pytest.fixture(autouse=True, scope="function")
def setup_and_teardown_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db():
    db = TestingSessionLocal()
    try:
        create_admin(db)  # Creates admin user in test DB
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture(scope="function")
def admin_token(client):
    res = client.post(
        "/auth/login",
        data={"username": 'admin@example.com', "password": "admin123"}
    )
    return res.json()["access_token"]

@pytest.fixture(scope="function")
def auth_headers(admin_token):
    return {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }

# ------------------- Book Tests -------------------

def test_create_book(client: TestClient, auth_headers):
    response = client.post(
        "/books/",
        json={"title": "Python 101", "author": "Guido", "isbn": "1234567890", "total_copies": 3},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Python 101"

def test_get_all_books(client: TestClient, auth_headers):
    response = client.get("/books", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_book_by_id(client: TestClient, auth_headers):
    create = client.post("/books", json={"title": "Django", "author": "Adrian", "isbn": "222", "total_copies": 2}, headers=auth_headers)
    book_id = create.json()["id"]
    response = client.get(f"/books/{book_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == book_id

def test_update_book(client: TestClient, auth_headers):
    create = client.post("/books", json={"title": "Old", "author": "A", "isbn": "333", "total_copies": 1}, headers=auth_headers)
    book_id = create.json()["id"]
    update = client.put(f"/books/{book_id}", json={"title": "New"}, headers=auth_headers)
    assert update.status_code == 200
    assert update.json()["title"] == "New"

def test_delete_book(client: TestClient, auth_headers):
    create = client.post("/books", json={"title": "Delete", "author": "A", "isbn": "444", "total_copies": 1}, headers=auth_headers)
    book_id = create.json()["id"]
    delete = client.delete(f"/books/{book_id}", headers=auth_headers)
    assert delete.status_code == 200
    assert delete.json()["detail"] == "Book deleted"

# ------------------- Mocking Examples -------------------

@patch("app.controllers.bookcontroller.borrow_service")
def test_borrow_book_mocked(mock_borrow_service, client: TestClient, auth_headers):
    mock_borrow_service.borrow_book.return_value = {"id": 1, "book_id": 1, "return_date": None}
    response = client.post("/borrow/", json={"book_id": 1}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == 1

@patch("app.controllers.bookcontroller.return_service")
def test_return_book_mocked(mock_return_service, client: TestClient, auth_headers):
    mock_return_service.return_book.return_value = {"id": 1, "book_id": 1, "return_date": "2025-06-06"}
    response = client.put("/borrow/1/return", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["return_date"] == "2025-06-06"

def test_borrow_history(client: TestClient, auth_headers):
    books = client.get("/books", headers=auth_headers).json()
    if books:
        book_id = books[0]["id"]
        response = client.get(f"/borrow/history/{book_id}", headers=auth_headers)
        assert response.status_code in [200, 404]  # Accept 404 if history is empty
