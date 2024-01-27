from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship


from .base_models import BaseModel
from .contact import Base #last

class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String(30), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    refresh_token = Column(String(255))
    contacts = relationship('Contact', back_populates='user')
    avatar = Column(String(), nullable=True)
    #Cloudinary public_id. It's also recommended to store by developers of cloudinary
    avatar_cld = Column(String(150), nullable=True)
    confirmed = Column(Boolean(), default=False, nullable=True)


