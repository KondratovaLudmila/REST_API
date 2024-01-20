from fastapi import APIRouter, HTTPException, Depends, status, Path
from typing import List, Annotated


from sqlalchemy.orm import Session
from pydantic import EmailStr


from src.dependencies.db import get_db
from src.dependencies.token_user import get_user_by_token
from src.repository.contacts_repo import ContactRepo
from src.schemas.contact_schema import ContactModel, ContactResponse
from src.models.user import User


router = APIRouter(prefix='/contacts', tags=["contacts"])

@router.get("/", response_model=List[ContactResponse])
async def cget_contacts(first_name: str=None, 
                        last_name: str=None, 
                        email: EmailStr=None, 
                        skip: int = 0, 
                        limit: int = 100,
                        user: User=Depends(get_user_by_token),
                        db: Session = Depends(get_db)):
    
    contacts = await ContactRepo(db, user).get_contacts(first_name, last_name, email, skip, limit)

    return contacts


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactModel, user: User=Depends(get_user_by_token), db: Session = Depends(get_db)):
    contact = await ContactRepo(db, user).create_contact(body)

    if contact is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                            detail="Contact with the same first name, last name and email allready exists")
    
    return contact


@router.get("/birthdays", response_model=List[ContactResponse])
async def get_birthdays(days: int=7,  user: User=Depends(get_user_by_token), db: Session = Depends(get_db)):
    contacts = await ContactRepo(db, user).get_birthdays(days)

    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: Annotated[int, Path(title="The ID of the item to get")],
                       user: User=Depends(get_user_by_token),
                      db: Session = Depends(get_db)):
    contact = await ContactRepo(db, user).get_contact(contact_id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contact not found")
    
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: Annotated[int, Path(title="The ID of the item to get")], 
                         body: ContactModel, 
                         user: User=Depends(get_user_by_token),
                         db: Session = Depends(get_db)):
    contact = await ContactRepo(db, user).update_contact(contact_id, body)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contact not found")
    
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def delete_contact(contact_id: Annotated[int, Path(title="The ID of the item to get")], 
                         user: User=Depends(get_user_by_token),
                         db: Session = Depends(get_db)):
    contact = await ContactRepo(db, user).delete_contact(contact_id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="contact not found")
    
    return contact