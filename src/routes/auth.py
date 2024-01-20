from fastapi import APIRouter, HTTPException, Depends, status, Security
from fastapi.security import OAuth2PasswordRequestForm,\
                            HTTPAuthorizationCredentials,\
                            HTTPBearer

from sqlalchemy.orm import Session


from src.dependencies.db import get_db
from src.servises.auth import auth_token
from src.servises.password_handler import pwd_handler
from src.repository.users_repo import UserRepo
from src.schemas.user_schema import UserModel, UserResponse, TokenModel


router = APIRouter(prefix='/auth', tags=["auth"])

security = HTTPBearer()

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user: UserModel, db: Session=Depends(get_db)):
    new_user = await UserRepo(db).create_user(user)
    if new_user is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="user is already exists")
    
    return new_user


@router.post("/signin", response_model=TokenModel)
async def signin(request_user: OAuth2PasswordRequestForm=Depends(), db: Session=Depends(get_db)) -> TokenModel:
    user_repo = UserRepo(db)
    cur_user = await user_repo.get_user_by_email(request_user.username)

    if cur_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    
    if not pwd_handler.verify_password(request_user.password, cur_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    
    access_token = await auth_token.create_access_token(data={"sub": cur_user.email})
    refresh_token = await auth_token.create_refresh_token(data={"sub": cur_user.email})

    await user_repo.update_refresh_token(cur_user, refresh_token)
    
    return {"access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"}
    

@router.get("/refresh_token", response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials=Security(security), db: Session=Depends(get_db)):
    token = credentials.credentials
    print(token)
    payload = await auth_token.get_payload(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    print(payload)
    user_repo = UserRepo(db)
    user = await user_repo.get_user_by_email(payload.get("sub", ""))

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    
    if user.refresh_token != token:
        await user_repo.update_refresh_token(user, None)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    access_token = await auth_token.create_access_token({"sub": user.email})
    refresh_token = await auth_token.create_refresh_token({"sub": user.email})

    await user_repo.update_refresh_token(user, refresh_token)

    return {"access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"}



    
    
    


