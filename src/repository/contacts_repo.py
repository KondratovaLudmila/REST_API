
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta, datetime
from sqlalchemy.sql import func, or_, and_, extract

from src.models.contact import Contact
from src.models.user import User
from src.schemas.contact_schema import ContactModel



class ContactRepo:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user


    async def get_contacts(self, 
                           first_name: str, 
                           last_name: str, 
                           email: str, 
                           skip: int, 
                           limit: int) -> List[Contact]:
        
        contacts = self.db.query(Contact).filter(Contact.user_id == self.user.id)
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
        
        contact = Contact(**contact.model_dump(), user=self.user)
        self.db.add(contact)
        self.db.commit()
        self.db.refresh(contact)
        
        return contact


    async def get_contact(self, pk: int) -> Contact:
        contact = self.db.query(Contact).get(pk)
        if contact.user_id == self.user.id:
            return contact
        else:
            return None


    async def update_contact(self, pk: int, contact: ContactModel) -> Contact:
        upd_contact = self.db.query(Contact).get(pk)

        if not upd_contact:
            return None
        
        if upd_contact.user_id != self.user.id:
            return None
        
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

        if not contact:
            return None

        if contact.user_id != self.user.id:
            return None

        self.db.delete(contact)
        self.db.commit()

        return contact


    async def get_birthdays(self, days: int) -> List[Contact]:
        start_date = datetime.now()
        
        dates = []
        for i in range(0,days + 1):
            delta = timedelta(days=i)
            new_date = start_date + delta
            dates.append(new_date.strftime("%d.%m"))

        contacts = self.db.query(Contact)\
            .where(and_(Contact.user_id == self.user.id, func.to_char(Contact.birth_date, "DD.MM").in_(dates)))\
            .all()
        
        return contacts
        
        
    async def get_unique_contact(self, contact: ContactModel):
        cont = self.db.query(Contact)\
            .filter_by(first_name = contact.first_name,
                        last_name = contact.last_name,
                        email = contact.email,
                        user_id = self.user.id)\
            .first()
        
        return cont