from typing import Any
from fastapi import (APIRouter, 
                     Depends, 
                     UploadFile, 
                     File,
                     Request,
                    )

from sqlalchemy.orm import Session


from src.dependencies.db import get_db
from src.dependencies.cache import get_cache
from src.dependencies.token_user import get_user_by_token
from src.models.user import User
from src.repository.users_repo import UserRepo
from src.schemas.user_schema import UserResponse


router = APIRouter(prefix='/users', tags=["users"])


@router.get("/me", response_model=UserResponse)
async def current_user(user: User=Depends(get_user_by_token),
                       db: Session=Depends(get_db)):
    """
    The current_user function returns the current signin in user.
    
    
    :param user: User: Get the user object from the get_user_by_token function
    :param db: Session: Pass the database session to the function
    :return: The UserResponse schema object
    :doc-author: Trelent
    """
    cur_user = await UserRepo(db).get_user_by_email(user.email)
    return cur_user


@router.patch("/avatar", response_model=UserResponse)
async def update_avatar(request: Request,
                        file: UploadFile=File(),
                        user: User=Depends(get_user_by_token),
                        cache: Any=Depends(get_cache),
                        db: Session = Depends(get_db)):
    """
    The update_avatar function updates the avatar of a user.
        The function takes in an UploadFile object, which is a file that has been uploaded to the server. 
        It also takes in a User object, which is obtained by calling get_user_by_token(). 
        This function returns an updated User object.
    
    :param file: UploadFile: Get the file from the request body
    :param user: User: Get the user's email from the token (Dependency injection)
    :param cache: Delete the user from the cache (Dependency injection)
    :param db: Session: Get the database session (Dependency injection)
    :return: A UserResponse schema object, which is the updated user
    :doc-author: Trelent
    """
    
    upd_user = await UserRepo(db).update_avatar(user.email, file.file)
    cache.delete(f"user:{user.email}")
    
    return upd_user