from sqlalchemy import Column, String, Date, UniqueConstraint
from .base_models import BaseModel, Base


class Contact(BaseModel):
    __tablename__ = "contacts"

    first_name = Column(String(30))
    last_name = Column(String(50))
    email = Column(String(30))
    phone = Column(String(25))
    birth_date = Column(Date)
    description = Column(String())

    __table_args__ = (UniqueConstraint(first_name, last_name, email, name="first_last_email"),)





