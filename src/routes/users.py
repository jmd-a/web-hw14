from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import User
from src.schemas import UserCreate
from src.security import get_password_hash
from src.repository import users

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    existing_user = await users.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    created_user = await users.create_user(user_data)
    return created_user