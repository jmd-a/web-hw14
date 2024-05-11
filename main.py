from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import date, timedelta
from typing import List
from faker import Faker


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SQLALCHEMY_DATABASE_URL = "postgresql://postgres:123456@localhost:5432/postgres"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    phone_number = Column(String)
    birthday = Column(Date)
    additional_info = Column(String, nullable=True)


Base.metadata.create_all(bind=engine)


class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: date
    additional_info: str = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(ContactBase):
    pass


class ContactInDB(ContactBase):
    id: int


app = FastAPI()


@app.get("/docs", include_in_schema=False)
async def docs():
    return templates.TemplateResponse("docs.html", {"request": "docs"})


@app.post("/contacts/", response_model=ContactInDB)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    db_contact = Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


@app.get("/contacts/", response_model=List[ContactInDB])
def read_contacts(
        skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return db.query(Contact).offset(skip).limit(limit).all()


@app.get("/contacts/{contact_id}", response_model=ContactInDB)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@app.put("/contacts/{contact_id}", response_model=ContactInDB)
def update_contact(
        contact_id: int, contact: ContactUpdate, db: Session = Depends(get_db)
):
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    for key, value in contact.dict().items():
        setattr(db_contact, key, value)
    db.commit()
    db.refresh(db_contact)
    return db_contact


@app.delete("/contacts/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(db_contact)
    db.commit()
    return {"message": "Contact deleted"}


@app.get("/contacts/search/")
def search_contacts(
        query: str = Query(..., min_length=3, description="Search query"),
        db: Session = Depends(get_db)
):
    return db.query(Contact).filter(
        or_(
            Contact.first_name.ilike(f"%{query}%"),
            Contact.last_name.ilike(f"%{query}%"),
            Contact.email.ilike(f"%{query}%")
        )
    ).all()


@app.get("/contacts/birthdays/")
def upcoming_birthdays(db: Session = Depends(get_db)):
    today = date.today()
    next_week = today + timedelta(days=7)
    return db.query(Contact).filter(
        extract('month', Contact.birthday) == today.month,
        extract('day', Contact.birthday) >= today.day,
        extract('day', Contact.birthday) <= next_week.day
    ).all()


fake = Faker()


@app.get("/generate_fake_data")
async def generate_fake_data():
    fake_data = {
        "name": fake.name(),
        "email": fake.email(),
        "phone_number": fake.phone_number(),
        "birthdate": fake.date_of_birth(minimum_age=18, maximum_age=90),
        "additional_info": fake.text()
    }
    return fake_data
