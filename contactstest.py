import sys
import os
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base, Contact
from src.repository.contacts import get_contacts, create_contact, update_contact, delete_contact

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestContactsRepository(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(bind=engine)
        cls.Session = sessionmaker(bind=engine)

    def setUp(self):
        self.session = self.Session()

    def tearDown(self):
        self.session.close()

    async def test_create_contact(self):
        new_contact = await create_contact(ContactCreate(name='John', surname='Doe', email='john@example.com'),
                                           db=self.session)
        self.assertIsInstance(new_contact, Contact)

    def test_create_contact(self):
        new_contact = create_contact(Contact(name='Jane', surname='Doe', email='jane@example.com'), db=self.session)
        self.assertIsInstance(new_contact, Contact)

        retrieved_contact = self.session.query(Contact).filter_by(email='jane@example.com').first()
        self.assertIsNotNone(retrieved_contact)


if __name__ == '__main__':
    unittest.main()
