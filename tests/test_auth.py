
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import User
from app.hashing import Hash

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_db.sqlite3"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Overriding the get_db dependency to use the testing database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def create_test_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)



def create_verified_user(db, email="ashwin@example.com", password="Ashwin@798724"):
    hashed_password = Hash.bcrypt(password)
    user = User(
        email=email,
        password=hashed_password,
        role="user",
        is_varified=True, ## jsut doing for testing purpose
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_signup_then_verify_and_login(client):
    # Signup
    signup_payload = {
        "name": "Bob",
        "email": "bob@example.com",
        "password": "Val1dP@ssword",
        "role": "user"
    }
    response = client.post("/auth/signup", json=signup_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Signup successful"

    # Verify with fixed OTP
    verify_payload = {
        "email": "bob@example.com",
        "otp": "1234"
    }
    response = client.post("/auth/verify", json=verify_payload)
    assert response.status_code == 200
    assert "access_token" in response.json()

    # Login
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
        "password": "ValidP@ss1",
        "role": "user"
    }
    client.post("/auth/signup", json=signup_payload)

    # Try verifying with wrong OTP
    verify_payload = {
        "email": "charlie@example.com",
        "otp": "0000"
    }
    response = client.post("/auth/verify", json=verify_payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired OTP"


def test_login_fails_when_user_does_not_exist():
    response = client.post(
        "/auth/login",
        data={"username": "nonexistent@example.com", "password": "irrelevant"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Invalid Credentials"


def test_login_fails_when_password_incorrect():
    # Creating a verified user manually via DB
    db = TestingSessionLocal()
    user = create_verified_user(db, email="dave@example.com", password="Strong1@Pass")
    db.close()

    # Attempt login with wrong password
    login_response = client.post(
        "/auth/login",
        data={"username": "dave@example.com", "password": "WrongPassword"}
    )
    assert login_response.status_code == 400
    assert login_response.json()["detail"] == "Incorrect password"


def test_signup_fails_if_email_already_registered(client):
    signup_payload = {
        "name": "Eve",
        "email": "eve@example.com",
        "password": "Str0ngP@ssword",
        "role": "user"
    }

    # First signup
    client.post("/auth/signup", json=signup_payload)

    # Second signup (same email)
    response = client.post("/auth/signup", json=signup_payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"
