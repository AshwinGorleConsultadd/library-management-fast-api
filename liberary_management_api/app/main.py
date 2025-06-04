from fastapi import FastAPI
from  app.blog import  models
from app.blog.database import engine
from app.blog.routers import user, auth, book

app = FastAPI()

models.Base.metadata.create_all(engine)

app.include_router(auth.router)
app.include_router(book.router)
app.include_router(user.router)
