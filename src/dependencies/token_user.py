from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.dependencies.db import get_db
from src.servises.auth import auth_token
from src.repository.users_repo import UserRepo
from src.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/signin")


async def get_user_by_token(token: str = Depends(oauth2_scheme), db: Session=Depends(get_db)) -> User:
    """If possible return user object by email encoded in jwt-token
        else raise HTTPException with status code 401

    Args:
        token (str, optional): encoded JWT-token string. Defaults to Depends(oauth2_scheme).
        db (Session, optional): database session object. Defaults to Depends(get_db).

    Raises:
        HTTPException: 401 invalid email
        HTTPException: 401 invalid token
        HTTPException: 401 invalid token scope

    Returns:
        User: user object from database
    """
    payload = await auth_token.get_payload(token)

    if not payload:
        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid token",
                            headers={"WWW-Authenticate": "Bearer"},
                            )
    
    if payload.get("scope", "") != "access_token":
        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid token scope",
                            headers={"WWW-Authenticate": "Bearer"},
                            )
    
    email = payload.get("sub", "")

    user = await UserRepo(db).get_user_by_email(email)

    if user:
        return user
    
    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid email",
                        headers={"WWW-Authenticate": "Bearer"},
                        )




    


