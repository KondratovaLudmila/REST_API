from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from typing import List, Annotated
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
from pydantic import EmailStr


from src.dependencies.db import get_db
from src.dependencies.token_user import get_user_by_token
from src.repository.contacts_repo import ContactRepo
from src.schemas.contact_schema import ContactModel, ContactResponse
from src.models.user import User

TIMES = 5
SECONDS = 60

router = APIRouter(prefix='/contacts', tags=["contacts"])

@router.get("/", 
            response_model=List[ContactResponse],
            description='No more than 5 requests per minute',
            dependencies=[Depends(RateLimiter(times=TIMES, seconds=SECONDS))])
async def get_contacts(first_name: str=None, 
                        last_name: str=None, 
                        email: EmailStr=None, 
                        skip: int = 0, 
                        limit: int = 100,
                        user: User=Depends(get_user_by_token),
                        db: Session = Depends(get_db)):
    """
    The cget_contacts function returns a list of contacts.
    
    :param first_name: str: Filter the contacts by first name
    :param last_name: str: Filter the contacts by last name
    :param email: EmailStr: Validate the email address
    :param skip: int: Skip a number of contacts in the database
    :param limit: int: Limit the number of contacts returned
    :param user: User: Get the user from the token
    :param db: Session: Pass the database session to the contactrepo class
    :return: A list of ContactResponse schema objects
    :doc-author: Trelent
    """
    
    contacts = await ContactRepo(db, user).get_contacts(first_name, last_name, email, skip, limit)

    return contacts


@router.post("/", 
             response_model=ContactResponse, 
             description='No more than 5 requests per minute',
             dependencies=[Depends(RateLimiter(times=TIMES, seconds=SECONDS))],
             status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactModel, user: User=Depends(get_user_by_token), db: Session = Depends(get_db)):
    """
    The create_contact function creates a new contact in the database.
    The function takes a ContactModel object as input and returns the created contact.
    
    
    :param body: ContactModel: Validate the data that is sent in the request body
    :param user: User: Get the user_id from the token
    :param db: Session: Pass the database session to the contactrepo class
    :return: A ContactResponse schema object
    :doc-author: Trelent
    """
    contact = await ContactRepo(db, user).create_contact(body)

    if contact is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                            detail="Contact with the same first name, last name and email allready exists")
    
    return contact


@router.get("/birthdays", 
            response_model=List[ContactResponse],
            description='No more than 5 requests per minute',
            dependencies=[Depends(RateLimiter(times=TIMES, seconds=SECONDS))])
async def get_birthdays(days: int=Query(default=7, gt=0, lt=10, description="Period in days started from current date"), 
                         user: User=Depends(get_user_by_token), db: Session = Depends(get_db)):
    """
    The get_birthdays function returns a list of contacts with birthdays in the next 7 days.
    
    :param days: int: Specify the period in days from 1 to 10 started from current date
    :param user: User: Get the user object from the token
    :param db: Session: Get the database session
    :return: A list of ContactResponse schema objects
    :doc-author: Trelent
    """
    
    contacts = await ContactRepo(db, user).get_birthdays(days)

    return contacts


@router.get("/{contact_id}", 
            response_model=ContactResponse,
            description='No more than 5 requests per minute',
            dependencies=[Depends(RateLimiter(times=TIMES, seconds=SECONDS))])
async def get_contact(contact_id: Annotated[int, Path(title="The ID of the item to get")],
                       user: User=Depends(get_user_by_token),
                       db: Session = Depends(get_db)):
    """
    The get_contact function returns a contact by its ID.
    
    :param contact_id: Annotated[int: Annotate the parameter with a type and title
    :param Path(title: Set the title of the parameter in swagger
    :param user: User: Get the user from the token
    :param db: Session: Pass the database session to the contactrepo class
    :return: A ContactResponse schema object
    :doc-author: Trelent
    """
    contact = await ContactRepo(db, user).get_contact(contact_id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contact not found")
    
    return contact


@router.put("/{contact_id}", 
            response_model=ContactResponse,
            description='No more than 5 requests per minute',
            dependencies=[Depends(RateLimiter(times=TIMES, seconds=SECONDS))]
            )
async def update_contact(contact_id: Annotated[int, Path(title="The ID of the item to get")], 
                         body: ContactModel, 
                         user: User=Depends(get_user_by_token),
                         db: Session = Depends(get_db)):
    """
    The update_contact function updates a contact in the database.
    
    :param contact_id: Get the contact id from the path
    :param body: ContactModel: Get the data from the request body
    :param user: User: Get the user from the token (Dependency injection)
    :param db: Session: Get a database session (Dependency injection)
    :return: A ContactResponse schema object
    :doc-author: Trelent
    """
    contact = await ContactRepo(db, user).update_contact(contact_id, body)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contact not found")
    
    return contact


@router.delete("/{contact_id}", 
               response_model=ContactResponse,
               description='No more than 5 requests per minute',
               dependencies=[Depends(RateLimiter(times=TIMES, seconds=SECONDS))])
async def delete_contact(contact_id: Annotated[int, Path(title="The ID of the item to get")], 
                         user: User=Depends(get_user_by_token),
                         db: Session = Depends(get_db)):
    """
    The delete_contact function deletes a contact from the database
    by it's ID
    
    :param contact_id: Annotated[int: Get the id of the contact to be deleted
    :param user: User: Get the user from the token (Dependency injection)
    :param db: Session: Pass the database session to the contactrepo class (Dependency injection)
    :return: A ContactResponse schema object
    :doc-author: Trelent
    """
    contact = await ContactRepo(db, user).delete_contact(contact_id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contact not found")
    
    return contact