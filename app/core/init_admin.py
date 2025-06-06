import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database import SessionLocal
from app.models import User

load_dotenv()

ADMIN_EMAIL = os.getenv("ADMIN_USERNAME", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_admin(db: Session = None):  # ✅ Make db optional
    if db is None:
        db = SessionLocal()  # use production DB
        own_session = True
    else:
        own_session = False

    existing = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if not existing:
        hashed_password = pwd_context.hash(ADMIN_PASSWORD)
        admin_user = User(
            name="Admin",
            email=ADMIN_EMAIL,
            password=hashed_password,
            role="admin",
            is_varified=True
        )
        db.add(admin_user)
        db.commit()
        print("✅ Admin user created!")
    else:
        print("⚠️  Admin user already exists.")

    if own_session:
        db.close()
