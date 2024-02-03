from collections.abc import Callable
from typing import Any
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, timedelta

from src.models.contact import Contact
from src.models.user import User, Base
from src.schemas.contact_schema import ContactModel, ContactResponse
from src.repository.contacts_repo import ContactRepo
import os
import dotenv

dotenv.load_dotenv()

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
port = os.getenv("POSTGRES_PORT")
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@localhost:{port}/tests"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def eq_contacts(cnt1: Contact, cnt2: Contact, msg=None):
    result = cnt1.first_name == cnt2.first_name and \
            cnt1.last_name == cnt2.last_name and \
            cnt1.email == cnt2.email and \
            cnt1.phone == cnt2.phone and \
            cnt1.birth_date == cnt2.birth_date and \
            cnt1.description == cnt2.description and \
            cnt1.user_id == cnt2.user_id
    
    return result


class TestContacts(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.session = TestingSessionLocal()

        #Add users
        user1 = User(email="user@i.ua", password="123")
        user2 = User(email="user2@i.ua", password="111")
        self.session.add(user1)
        self.session.add(user2)

        #Add contacts
        cur_month = date.today().month
        cur_day = date.today().day

        contact1 = Contact(
                          first_name="Grigorij", 
                          last_name="Skovoroda", 
                          email="grisha_ne_patelnya@gmail.com",
                          birth_date=date(year=1722, month=cur_month, day=cur_day),
                          user=user1
                          )
        delta = timedelta(days=1)
        contact2 = Contact(
                          first_name="Lesya", 
                          last_name="Ukrainka", 
                          email="ukrlara@gmail.com",
                          birth_date=date(year=1871, month=cur_month, day=cur_day) + delta,
                          user=user1
                          )
        delta = timedelta(days=11)
        contact3 = Contact(
                          first_name="Yaroslav", 
                          last_name="Mudryi", 
                          email="ya_mudryi@gmail.com",
                          birth_date=date(year=1054, month=cur_month, day=cur_day) + delta,
                          user=user2
                          )
        
        self.session.add(contact1)
        self.session.add(contact2)
        self.session.add(contact3)
        self.session.commit()

        self.users = [user1, user2]
        self.contacts = [contact1, contact2, contact3]

        self.addTypeEqualityFunc(Contact, eq_contacts)
        
    
    def tearDown(self) -> None:
        self.session.close()
        Base.metadata.drop_all(bind=engine)


    async def test_get_contacts_without_args(self):
        user = self.users[0]
        result = await ContactRepo(db=self.session, user=user).get_contacts(first_name=None, 
                                                                             last_name=None,
                                                                             email= None, 
                                                                             skip=0, 
                                                                             limit=10)
        
        self.assertListEqual(result, self.contacts[0:2])


    async def test_get_contacts_by_first_name(self):
        contact = self.contacts[1]
        user = self.users[0]
        result = await ContactRepo(db=self.session, user=user).get_contacts(first_name=contact.first_name,
                                                                                     last_name=None,
                                                                                     email=None,
                                                                                     skip=0, 
                                                                                     limit=10)
        self.assertListEqual(result, [contact,])


    async def test_get_contacts_by_last_name(self):
        contact = self.contacts[1]
        user = self.users[0]
        result = await ContactRepo(db=self.session, user=user).get_contacts(first_name=None,
                                                                            last_name=contact.last_name,
                                                                            email=None,
                                                                            skip=0, 
                                                                            limit=10)
        self.assertListEqual(result, [contact,])


    async def test_get_contacts_by_email(self):
        contact = self.contacts[1]
        user = self.users[0]
        result = await ContactRepo(db=self.session, user=user).get_contacts(first_name=None,
                                                                            last_name=None,
                                                                            email=contact.email,
                                                                            skip=0, 
                                                                            limit=10)
        self.assertListEqual(result, [contact,])


    async def test_get_contacts_by_all(self):
        contact = self.contacts[1]
        user = self.users[0]
        result = await ContactRepo(db=self.session, user=user).get_contacts(first_name=contact.first_name,
                                                                            last_name=contact.last_name,
                                                                            email=contact.email,
                                                                            skip=0, 
                                                                            limit=10)
        self.assertListEqual(result, [contact,])


    async def test_get_contacts_not_found(self):
        contact = self.contacts[1]
        user = self.users[1]
        result = await ContactRepo(db=self.session, user=user).get_contacts(first_name=contact.first_name,
                                                                            last_name=contact.last_name,
                                                                            email=contact.email,
                                                                            skip=0, 
                                                                            limit=10)
        self.assertListEqual(result, [])


    async def test_get_contacts_skip(self):
        user = self.users[0]
        skip = 1
        result = await ContactRepo(db=self.session, user=user).get_contacts(first_name=None, 
                                                                             last_name=None,
                                                                             email= None, 
                                                                             skip=skip, 
                                                                             limit=10)
        
        self.assertListEqual(result, self.contacts[1:2])


    async def test_get_contacts_limit(self):
        user = self.users[0]
        limit = 1
        result = await ContactRepo(db=self.session, user=user).get_contacts(first_name=None, 
                                                                             last_name=None,
                                                                             email= None, 
                                                                             skip=0, 
                                                                             limit=limit)
        
        self.assertListEqual(result, self.contacts[0:1])
    

    async def test_create_contact(self):
        user = self.users[0]
        
        contact = ContactModel(first_name="Bohdan", 
                               last_name="Khmelniskyi", 
                               email="bohdan_1595@gmail.com",
                               phone="5658587876",
                               birth_date=date(year=1596, month=1, day=6),
                               description="test")
        result = await ContactRepo(db=self.session, user=user).create_contact(contact)
        
        self.assertEqual(result, Contact(**contact.model_dump(), user=user))


    async def test_create_contact_duplicate(self):
        user = self.users[0]
        contact = self.contacts[1]
        duplicate = ContactModel(first_name=contact.first_name, 
                                 last_name=contact.last_name, 
                                 email=contact.email,
                                 phone="098009880",
                                 birth_date=date(year=1596, month=1, day=6),
                                 description=None)
        result = await ContactRepo(db=self.session, user=user).create_contact(duplicate)
        
        self.assertIsNone(result)


    async def test_create_contact_duplicate_diff_user(self):
        user = self.users[1]
        contact = self.contacts[1]
        duplicate = ContactModel(first_name=contact.first_name, 
                                 last_name=contact.last_name, 
                                 email=contact.email,
                                 phone="098009880",
                                 birth_date=date(year=1596, month=1, day=6),
                                 description=None)
        result = await ContactRepo(db=self.session, user=user).create_contact(duplicate)
        
        self.assertIsNotNone(result)


    async def test_get_contact_found(self):
        user = self.users[0]
        contact = self.contacts[1]

        result = await ContactRepo(db=self.session, user=user).get_contact(contact.id)

        self.assertEqual(result, contact)


    async def test_get_contact_not_found_by_user(self):
        user = self.users[1]
        contact = self.contacts[1]

        result = await ContactRepo(db=self.session, user=user).get_contact(contact.id)

        self.assertIsNone(result)


    async def test_get_contact_not_found_by_id(self):
        user = self.users[0]
        pk = 10

        result = await ContactRepo(db=self.session, user=user).get_contact(pk)

        self.assertIsNone(result)


    async def test_update_contact(self):
        user = self.users[0]
        pk = 2
        contact = ContactModel(first_name="Bohdan", 
                               last_name="Khmelniskyi", 
                               email="bohdan_1595@gmail.com",
                               phone="5658587876",
                               birth_date=date(year=1596, month=1, day=6),
                               description="test")
        
        result = await ContactRepo(db=self.session, user=user).update_contact(pk, contact)

        self.assertEqual(result, Contact(**contact.model_dump(), user=user))


    async def test_update_contact_wrong_user(self):
        user = self.users[0]
        pk = 3
        contact = ContactModel(first_name="Bohdan", 
                               last_name="Khmelniskyi", 
                               email="bohdan_1595@gmail.com",
                               phone="5658587876",
                               birth_date=date(year=1596, month=1, day=6),
                               description="test")
        
        result = await ContactRepo(db=self.session, user=user).update_contact(pk, contact)

        self.assertIsNone(result)


    async def test_update_contact_wrong_id(self):
        user = self.users[0]
        pk = 10
        contact = ContactModel(first_name="Bohdan", 
                               last_name="Khmelniskyi", 
                               email="bohdan_1595@gmail.com",
                               phone="5658587876",
                               birth_date=date(year=1596, month=1, day=6),
                               description="test")
        
        result = await ContactRepo(db=self.session, user=user).update_contact(pk, contact)

        self.assertIsNone(result)


    async def test_delete_contact(self):
        user = self.users[0]
        pk = 2
        contact = self.contacts[1]
        
        result = await ContactRepo(db=self.session, user=user).delete_contact(pk)

        #Expected contact returned
        self.assertEqual(result, contact)
        #Contact is already deleted
        self.assertIsNone(self.session.get(Contact, pk))


    async def test_update_contact_wrong_user(self):
        user = self.users[0]
        pk = 3
        contact = self.contacts[2]
        
        result = await ContactRepo(db=self.session, user=user).delete_contact(pk)

        #Any contact is not returned
        self.assertIsNone(result)
        #Contact exists and not changed
        self.assertEqual(self.session.get(Contact, pk), contact)


    async def test_update_contact_wrong_id(self):
        user = self.users[0]
        pk = 10
        
        result = await ContactRepo(db=self.session, user=user).delete_contact(pk)

        self.assertIsNone(result)


    async def test_get_birthdays(self):
        user = self.users[0]
        contacts = self.contacts[0:2]
        days = 2
        
        result = await ContactRepo(db=self.session, user=user).get_birthdays(days)

        self.assertListEqual(result, contacts)


    async def test_get_birthdays_over_limit(self):
        user = self.users[1]
        days = 20
        
        result = await ContactRepo(db=self.session, user=user).get_birthdays(days)

        self.assertEqual(result, [])


    async def test_get_unique_contact_found(self):
        user = self.users[0]
        contact = self.contacts[1]
        
        result = await ContactRepo(db=self.session, user=user).get_unique_contact(contact)
        
        self.assertEqual(result, contact)


    async def test_get_unique_contact_not_found(self):
        user = self.users[0]
        contact = self.contacts[2]
        
        result = await ContactRepo(db=self.session, user=user).get_unique_contact(contact)
        
        self.assertIsNone(result)
        


if __name__ == '__main__':
    unittest.main()
