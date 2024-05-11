from sqlalchemy.orm import Session
from typing import List, Optional
from src.database.models import Contact
from src.schemas import ContactCreate, ContactUpdate
from datetime import date, timedelta


def get_contacts(skip: int = 0, limit: int = 100, db: Session = None) -> List[Contact]:
    return db.query(Contact).offset(skip).limit(limit).all()


def get_contact(contact_id: int, db: Session = None) -> Optional[Contact]:
    return db.query(Contact).filter(Contact.id == contact_id).first()


def create_contact(contact: ContactCreate, db: Session = None) -> Contact:
    new_contact = Contact(**contact.dict())
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact


def update_contact(contact_id: int, contact_update: ContactUpdate, db: Session = None) -> Contact:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        for field, value in contact_update.dict(exclude_unset=True).items():
            setattr(contact, field, value)
        db.commit()
        db.refresh(contact)
    return contact


def delete_contact(contact_id: int, db: Session = None):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
        return contact


def search_contacts(query: str, db: Session = None) -> List[Contact]:
    return db.query(Contact).filter(
        db.or_(
            Contact.name.ilike(f"%{query}%"),
            Contact.surname.ilike(f"%{query}%"),
            Contact.email.ilike(f"%{query}%"),
        )
    ).all()


def get_upcoming_birthdays(db: Session = None) -> List[Contact]:
    today = date.today()
    next_week = today + timedelta(days=7)
    return db.query(Contact).filter(
        db.or_(
            db.and_(Contact.birthday.month == today.month, Contact.birthday.day >= today.day),
            db.and_(Contact.birthday.month == next_week.month, Contact.birthday.day <= next_week.day),
        )
    ).all()
