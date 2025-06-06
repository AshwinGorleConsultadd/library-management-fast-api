import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.core.init_admin import create_admin
from dotenv import load_dotenv

load_dotenv()

# DB setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_db.sqlite3"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

ADMIN_EMAIL = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

@pytest.fixture(autouse=True, scope="function")
def setup_and_teardown_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db():
    db = TestingSessionLocal()
    try:
        create_admin(db)  # ✅ Creates admin user in test DB
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

# Begin tests using admin only

def test_admin_login_success(client):
    response = client.post(
        "/auth/login",
        data={"username": "admin@example.com", "password": "admin123"}  # ✅ Correct format
    )

    print("response---", response.json())
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_signup_then_verify_and_login(client):
    # check Signup
    signup_payload = {
        "name": "Bob",
        "email": "bob@example.com",
        "password": "Val1dP@ssword"
    }
    response = client.post("/auth/signup", json=signup_payload)
    assert response.status_code == 200
    assert response.json()["message"] == "Signup successful"

    #check varify
    verify_payload = {
        "email": "bob@example.com",
        "otp": "1234"
    }
    response = client.post("/auth/varify_email", json=verify_payload)
    assert response.status_code == 200
    assert "access_token" in response.json()

    # check login
    login_response = client.post(
        "/auth/login",
        data={"username": "bob@example.com", "password": "Val1dP@ssword"}
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()

def test_verify_with_invalid_otp_fails(client):
    # Signup
    signup_payload = {
        "name": "Charlie",
        "email": "charlie@example.com",
        "password": "ValidP@ss1"
    }
    client.post("/auth/signup", json=signup_payload)
    # keeping Invalid OTP
    verify_payload = {
        "email": "charlie@example.com",
        "otp": "0000"
    }
    response = client.post("/auth/varify_email", json=verify_payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired OTP"

def test_login_fails_when_user_does_not_exist(client):
    response = client.post(
        "/auth/login",
        data={"username": "nonexistent@example.com", "password": "irrelevant"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Invalid Credentials"

def test_login_fails_when_password_incorrect(client):
    # Attempting login with wrong password for admin
    login_response = client.post(
        "/auth/login",
        data={"username": "admin@example.com", "password": "WrongPassword"}
    )
    assert login_response.status_code == 400
    assert login_response.json()["detail"] == "Incorrect password"

def test_signup_fails_if_email_already_registered(client):
    signup_payload = {
        "name": "Eve",
        "email": "eve@example.com",
        "password": "Str0ngP@ssword"
    }

    # First signup
    client.post("/auth/signup", json=signup_payload)

    # Second signup with same email
    response = client.post("/auth/signup", json=signup_payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"
