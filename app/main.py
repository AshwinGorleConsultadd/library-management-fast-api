from fastapi import FastAPI
from app import models
from app.database import engine
from app.routers import auth
from app.routers import book, user
from app.core.init_admin import create_admin


app = FastAPI()



create_admin()

models.Base.metadata.create_all(engine)

app.include_router(auth.router)
app.include_router(book.router)
app.include_router(user.router)
