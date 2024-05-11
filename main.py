from fastapi import FastAPI

from src.routes import contacts
from src.routes import users

app = FastAPI()

app.include_router(contacts.router, prefix='/api')
app.include_router(users.router, prefix='/users')

@app.get("/")
def read_root():
    return {"message": "Hello World"}