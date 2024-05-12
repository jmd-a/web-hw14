from fastapi import APIRouter, HTTPException, Query, Depends, Header
from datetime import date, timedelta
from src.database.models import Contact
from src.schemas import ContactBase, ContactCreate, ContactUpdate
from typing import List
from src.security import get_current_user_token

router = APIRouter()

contacts_db = []


@router.post("/contacts/")
async def create_contact(contact: ContactCreate, token: str = Depends(get_current_user_token)):
    return await contacts.create_contact(contact=contact, token=token)


@router.get("/contacts/")
async def get_all_contacts():
    return contacts_db


@router.get("/contacts/{contact_id}")
async def get_contact(contact_id: int):
    for contact in contacts_db:
        if contact.id == contact_id:
            return contact
    raise HTTPException(status_code=404, detail="Contact not found")


@router.put("/contacts/{contact_id}")
async def update_contact(contact_id: int, contact_update: ContactUpdate):
    for contact in contacts_db:
        if contact.id == contact_id:
            contact_data = contact_update.dict(exclude_unset=True)
            for key, value in contact_data.items():
                setattr(contact, key, value)
            return contact
    raise HTTPException(status_code=404, detail="Contact not found")


@router.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: int):
    for index, contact in enumerate(contacts_db):
        if contact.id == contact_id:
            del contacts_db[index]
            return {"message": "Contact deleted successfully"}
    raise HTTPException(status_code=404, detail="Contact not found")


@router.get("/contacts/search/")
async def search_contacts(query: str = Query(..., min_length=3)):
    search_result = []
    for contact in contacts_db:
        if query.lower() in contact.name.lower() or query.lower() in contact.surname.lower() or query.lower() in contact.email.lower():
            search_result.append(contact)
    return search_result


@router.get("/contacts/birthdays/")
async def get_upcoming_birthdays():
    today = date.today()
    next_week = today + timedelta(days=7)
    upcoming_birthdays = [contact for contact in contacts_db if
                          contact.birthday.month == today.month and contact.birthday.day >= today.day or contact.birthday.month == next_week.month and contact.birthday.day <= next_week.day]
    return upcoming_birthdays
