from fastapi import HTTPException, status
from src.security import decode_token
from src.database.models import Contact
from src.database.db import SessionLocal
from src.database.models import User
from src.schemas import UserCreate


def check_contact_access(contact_id: int, token: str):
    db = SessionLocal()
    try:
        payload = decode_token(token)
        user_id = payload.get("user_id")
        contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user_id).first()
        if not contact:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
        return contact
    finally:
        db.close()


async def get_user_by_email(email: str):
    db = SessionLocal()
    return db.query(User).filter(User.email == email).first()


async def create_user(user_data: UserCreate) -> User:
    db = SessionLocal()
    user = User(email=user_data.email, hashed_password=user_data.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
