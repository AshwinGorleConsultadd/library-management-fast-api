from fastapi import FastAPI
from app import models
from app.database import engine
from app.routers import auth
from app.routers import book, user, issue
from app.core.init_admin import create_admin
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from app.routers import member
import os

models.Base.metadata.create_all(engine)
app = FastAPI()
load_dotenv() 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_admin()
app.include_router(auth.router)
app.include_router(book.router)
app.include_router(user.router)
app.include_router(member.router)
app.include_router(issue.router)