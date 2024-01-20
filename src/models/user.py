from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from .base_models import BaseModel
from .contact import Base #last

class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String(30), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    refresh_token = Column(String(255))
    contacts = relationship('Contact', back_populates='user')


