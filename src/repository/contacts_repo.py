
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
        """
        The get_contacts function returns a list of contacts that match the given criteria.
        If the user_id of that contact matches with the current user's id, then
        it will return that contact object.
        
        :param self: Refer to the instance of the class
        :param first_name: str: Filter the contacts by first name
        :param last_name: str: Filter the contacts by last name
        :param email: str: Filter the contacts by email
        :param skip: int: Skip the first n contacts
        :param limit: int: Limit the number of contacts returned
        :return: A list of Contact objects matching the query parameters
        :doc-author: Trelent
        """
        
        contacts = self.db.query(Contact).filter(Contact.user_id == self.user.id)
        if first_name is not None:
            contacts = contacts.filter(Contact.first_name == first_name)
        if last_name is not None:
            contacts = contacts.filter(Contact.last_name == last_name)
        if email is not None:
            contacts = contacts.filter(Contact.email == email)
        
        return contacts.offset(skip).limit(limit).all()


    async def create_contact(self, contact: ContactModel) -> Contact:
        """
        The create_contact function creates a new contact in the database
        that belongs to current user
        
        :param self: Access the user's information
        :param contact: ContactModel: Create a new contact
        :return: A Contact object
        :doc-author: Trelent
        """
        unique = await self.get_unique_contact(contact) is None
        if not unique:
            return None
        
        contact = Contact(**contact.model_dump(), user=self.user)
        self.db.add(contact)
        self.db.commit()
        self.db.refresh(contact)
        
        return contact


    async def get_contact(self, pk: int) -> Contact:
        """
        The get_contact function returns a contact object from the database.
        If the user_id of that contact matches with the current user's id, then
        it will return that contact object.
        
        :param self: Represent the instance of the class
        :param pk: int: Get the contact from the database
        :return: A Contact object if the user_id matches
        :doc-author: Trelent
        """
        contact = self.db.get(Contact, pk)

        if contact is None:
            return None
        
        if contact.user_id == self.user.id:
            return contact
        else:
            return None


    async def update_contact(self, pk: int, contact: ContactModel) -> Contact:
        """
        The update_contact function updates a contact in the database.
        If the user_id of that contact matches with the current user's id, then
        it will return that contact object.
        
        :param self: Access the class attributes
        :param pk: int: Identify the contact to update
        :param contact: ContactModel: Pass the updated contact data to the function
        :return: The updated Contact object
        :doc-author: Trelent
        """
        upd_contact = self.db.get(Contact, pk)

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
        """
        The delete_contact function deletes a contact from the database.
        If the user_id of that contact matches with the current user's id, then
        it will delete contact and return that contact object.
        
        :param self: Represent the instance of the class
        :param pk: int: Specify the primary key of the contact to be deleted
        :return: The deleted Contact object
        :doc-author: Trelent
        """
        contact = self.db.get(Contact, pk)

        if not contact:
            return None

        if contact.user_id != self.user.id:
            return None

        self.db.delete(contact)
        self.db.commit()

        return contact


    async def get_birthdays(self, days_count: int) -> List[Contact]:
        """
        The get_birthdays function returns a list of contacts whose 
        birthdays are within the next `days` days.
        
        :param self: Refer to the class instance itself
        :param days: int: Specify how many days in the future to look for birthdays
        :return: A list of Contact objects
        :doc-author: Trelent
        """
        start_date = datetime.now()
        days = days_count if days_count < 10 else 10
        dates = []
        for i in range(0,days):
            delta = timedelta(days=i)
            new_date = start_date + delta
            dates.append(new_date.strftime("%d.%m"))

        contacts = self.db.query(Contact)\
            .where(and_(Contact.user_id == self.user.id, func.to_char(Contact.birth_date, "DD.MM").in_(dates)))\
            .all()
        
        return contacts
        
        
    async def get_unique_contact(self, contact: Contact | ContactModel):
        cont = self.db.query(Contact)\
            .filter_by(first_name = contact.first_name,
                        last_name = contact.last_name,
                        email = contact.email,
                        user_id = self.user.id)\
            .first()
        
        return cont