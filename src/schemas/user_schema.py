from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserModel(BaseModel):
    username: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    avatar: str | None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserCreatedResponse(BaseModel):
    user: UserResponse
    detail: str="User successfully created. Check your email for confirmation."

class UserUpdatePassword(BaseModel):
    curr_password: str
    new_password: str


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserMail(BaseModel):
    email: EmailStr


class PasswordResponse(BaseModel):
    result: bool
    detail: str


class ResetPassword(BaseModel):
    token: str
    password: str