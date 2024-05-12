from sqlalchemy.orm import Session
from typing import List, Optional
from src.database.models import Contact
from src.schemas import ContactCreate, ContactUpdate
from datetime import date, timedelta
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

"""
Contacts Repository Module
==========================

This module contains functions and classes related to managing contacts.

"""


def get_contacts(skip: int = 0, limit: int = 100, db: Session = None) -> List[Contact]:
    """
    Retrieve a list of contacts from the database.

    Args:
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.
        db (Session): SQLAlchemy database session.

    Returns:
        List[Contact]: A list of Contact objects retrieved from the database.
    """
    return db.query(Contact).offset(skip).limit(limit).all()


def get_contact(contact_id: int, db: Session = None) -> Optional[Contact]:
    return db.query(Contact).filter(Contact.id == contact_id).first()


async def create_contact(contact: ContactCreate, db: Session = None, token: str = "") -> Contact:
    await FastAPILimiter.check(f"limit_create_contact_{token}", limit=10, period=60)

    new_contact = Contact(**contact.dict())
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact


def update_contact(contact_id: int, contact_update: ContactUpdate, db: Session = None) -> Contact:
    """
    Оновлює контакт у базі даних за заданим ідентифікатором.

    :param contact_id: Ідентифікатор контакту, який потрібно оновити.
    :type contact_id: int
    :param contact_update: Об'єкт, що містить оновлені дані для контакту.
    :type contact_update: ContactUpdate
    :param db: Сесія бази даних, яку слід використовувати для здійснення операції оновлення.
               Якщо не вказано, буде використано зовнішню сесію.
    :type db: Session, optional
    :return: Оновлений об'єкт контакту.
    :rtype: Contact
    """
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
