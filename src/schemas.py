from datetime import date
from typing import Optional, List
from pydantic import BaseModel, EmailStr


class ContactBase(BaseModel):
    name: str
    surname: str
    email: EmailStr
    phone_number: str
    birthday: date
    aditional: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(ContactBase):
    pass


class UserCreate(BaseModel):
    email: EmailStr
    password: str
