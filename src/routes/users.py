from fastapi import (APIRouter, 
                     Depends, 
                     UploadFile, 
                     File,
                    )

from sqlalchemy.orm import Session
from pydantic import EmailStr


from src.dependencies.db import get_db
from src.dependencies.cache import get_cache
from src.dependencies.token_user import get_user_by_token
from src.models.user import User
from src.repository.users_repo import UserRepo
from src.schemas.user_schema import UserResponse


router = APIRouter(prefix='/users', tags=["users"])


@router.patch("/me", response_model=UserResponse)
async def current_user(user: User=Depends(get_user_by_token),
                       db: Session=Depends(get_db)):
    cur_user = await UserRepo(db).get_user_by_email(user.email)
    return cur_user


@router.patch("/avatar", response_model=UserResponse)
async def update_avatar(file: UploadFile=File(), 
                        user: User=Depends(get_user_by_token),
                        cache=Depends(get_cache),
                        db: Session = Depends(get_db)):

    upd_user = await UserRepo(db).update_avatar(user.email, file.file)
    cache.delete(f"user:{user.email}")
    
    return upd_user