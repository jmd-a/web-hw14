import sys
import os
import pytest
from sqlalchemy.orm import Session
from fastapi import FastAPI
from starlette.testclient import TestClient
from src.database.models import Contact
from src.schemas import ContactCreate
from main import app
from src.database.db import get_db
from sqlalchemy.orm import Session
from src.database.models import Base
from src.database.db import SessionLocal

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def client():
    def override_get_db():

        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db():
    return SessionLocal()


def test_create_contact(client, db):
    # Given
    new_contact_data = {
        "name": "John",
        "surname": "Doe",
        "email": "john.doe@example.com",
        "phone_number": "123456789",
        "birthday": "1990-01-01"
    }
    new_contact = ContactCreate(**new_contact_data)

    response = client.post("/contacts/", json=new_contact_data)

    assert response.status_code == 200
    assert response.json()["name"] == new_contact_data["name"]
    assert response.json()["surname"] == new_contact_data["surname"]
    assert response.json()["email"] == new_contact_data["email"]