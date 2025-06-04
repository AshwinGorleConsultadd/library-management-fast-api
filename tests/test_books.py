import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import User
from app.hashing import Hash


@pytest.fixture
def create_admin_user(db: Session):
    user = User(
        name="Admin",
        email="admin@example.com",
        password=Hash.bcrypt("AdminP@ss1"),
        role="admin",
        is_varified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_token(client: TestClient, create_admin_user):
    res = client.post(
        "/auth/login",
        data={"username": create_admin_user.email, "password": "AdminP@ss1"}
    )
    return res.json()["access_token"]


@pytest.fixture
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


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
    response = client.get("/books/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_book_by_id(client: TestClient, auth_headers):
    create = client.post("/books/", json={"title": "Django", "author": "Adrian", "isbn": "222", "total_copies": 2}, headers=auth_headers)
    book_id = create.json()["id"]
    response = client.get(f"/books/{book_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == book_id

def test_update_book(client: TestClient, auth_headers):
    create = client.post("/books/", json={"title": "Old", "author": "A", "isbn": "333", "total_copies": 1}, headers=auth_headers)
    book_id = create.json()["id"]
    update = client.put(f"/books/{book_id}", json={"title": "New"}, headers=auth_headers)
    assert update.status_code == 200
    assert update.json()["title"] == "New"

def test_delete_book(client: TestClient, auth_headers):
    create = client.post("/books/", json={"title": "Delete", "author": "A", "isbn": "444", "total_copies": 1}, headers=auth_headers)
    book_id = create.json()["id"]
    delete = client.delete(f"/books/{book_id}", headers=auth_headers)
    assert delete.status_code == 200
    assert delete.json()["detail"] == "Book deleted"


def test_borrow_and_return_book(client: TestClient, auth_headers, db: Session, create_admin_user):
    create = client.post("/books/", json={"title": "Borrow Me", "author": "X", "isbn": "555", "total_copies": 2}, headers=auth_headers)
    book_id = create.json()["id"]
    borrow = client.post("/borrow/", json={"book_id": book_id}, headers=auth_headers)
    assert borrow.status_code == 200
    borrow_id = borrow.json()["id"]
    ret = client.put(f"/borrow/{borrow_id}/return", headers=auth_headers)
    assert ret.status_code == 200
    assert ret.json()["return_date"] is not None


def test_borrow_history(client: TestClient, auth_headers):
    books = client.get("/books/", headers=auth_headers).json()
    if books:
        book_id = books[0]["id"]
        response = client.get(f"/borrow/history/{book_id}", headers=auth_headers)
        assert response.status_code in [200, 404]  # Accept 404 if history is empty
