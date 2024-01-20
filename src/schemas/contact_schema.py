from pydantic import BaseModel, PastDate, Field, EmailStr
from datetime import datetime

from .user_schema import UserResponse


class ContactModel(BaseModel):
    first_name: str = Field(max_length=30)
    last_name: str = Field(max_length=50)
    email: EmailStr
    phone: str = Field(None, pattern="^\+?\d{6,12}$")
    birth_date: PastDate | None
    description: str | None
    

class ContactResponse(ContactModel):
    id: int
    first_name: str 
    last_name: str
    email: str
    phone: str
    birth_date: PastDate | None
    description: str | None
    user: UserResponse
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attriutes = True


