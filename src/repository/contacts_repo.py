
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta, date
from sqlalchemy.sql import func, or_

from src.database.models import Contact
from src.schemas.contact_schema import ContactModel



class ContactRepo:
    def __init__(self, db: Session):
        self.db = db


    async def get_contacts(self, 
                           first_name: str, 
                           last_name: str, 
                           email: str, 
                           skip: int, 
                           limit: int) -> List[Contact]:
        
        contacts = self.db.query(Contact)
        if first_name is not None:
            contacts = contacts.filter(Contact.first_name == first_name)
        if last_name is not None:
            contacts = contacts.filter(Contact.last_name == last_name)
        if email is not None:
            contacts = contacts.filter(Contact.email == email)
        
        return contacts.offset(skip).limit(limit).all()


    async def create_contact(self, contact: ContactModel) -> Contact:
        unique = await self.get_unique_contact(contact) is None
        if not unique:
            return None
        
        contact = Contact(**contact.model_dump())
        self.db.add(contact)
        self.db.commit()
        self.db.refresh(contact)
        
        return contact


    async def get_contact(self, pk: int) -> Contact:
        contact = self.db.query(Contact).get(pk)

        return contact


    async def update_contact(self, pk: int, contact: ContactModel) -> Contact:
        upd_contact = self.db.query(Contact).get(pk)

        if upd_contact:
            upd_contact.first_name = contact.first_name
            upd_contact.last_name = contact.last_name
            upd_contact.email = contact.email
            upd_contact.birth_date = contact.birth_date
            upd_contact.phone = contact.phone
            upd_contact.description = contact.description

            self.db.commit()

        return upd_contact

    async def delete_contact(self, pk: int) -> Contact:
        contact = self.db.query(Contact).get(pk)

        if contact:
            self.db.delete(contact)
            self.db.commit()

        return contact

    async def get_birthdays(self, days: int) -> List[Contact]:
        delta = timedelta(days=days)
        start_date = date.today()
        end_date = start_date + delta

        year_delta = timedelta(days=365)

        contacts = self.db.query(Contact)\
            .where(or_((Contact.birth_date+func.age(Contact.birth_date)).between(start_date, end_date),
                       (Contact.birth_date+func.age(Contact.birth_date)+year_delta).between(start_date, end_date)))\
            .all()
        
        
        return contacts
        
        


    async def get_unique_contact(self, contact: ContactModel):
        cont = self.db.query(Contact).filter_by(first_name = contact.first_name,
                                                 last_name = contact.last_name,
                                                 email = contact.email).first()
        
        return cont