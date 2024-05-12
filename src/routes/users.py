from fastapi import APIRouter, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import User
from src.schemas import UserCreate
from src.security import get_password_hash
from src.repository import users
import cloudinary.uploader
import os

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    existing_user = await users.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    created_user = await users.create_user(user_data)
    return created_user


cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)


@router.post("/users/{user_id}/avatar")
async def upload_avatar(user_id: int, file: UploadFile = File(...)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    response = cloudinary.uploader.upload(file.file)

    user.avatar_url = response['secure_url']
    db.commit()

    return {"message": "Avatar updated successfully"}
