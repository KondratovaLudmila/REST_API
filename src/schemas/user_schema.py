from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class UserModel(BaseModel):
    username: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attriutes = True


class UserUpdatePassword(BaseModel):
    curr_password: str
    new_password: str


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
