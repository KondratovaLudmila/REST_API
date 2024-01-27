from fastapi import (APIRouter,
                    HTTPException, 
                    Depends, 
                    status, 
                    Security, 
                    BackgroundTasks, 
                    Request,
                    )
from fastapi.security import (OAuth2PasswordRequestForm,
                            HTTPAuthorizationCredentials,
                            HTTPBearer,
                            )

from sqlalchemy.orm import Session
from datetime import datetime


from src.dependencies.db import get_db
from src.servises.auth import auth_token
from src.servises.hash_handler import pwd_handler
from src.repository.users_repo import UserRepo
from src.schemas.user_schema import (UserModel, 
                                    UserCreatedResponse,
                                    TokenModel, 
                                    UserMail, 
                                    ResetPassword, 
                                    PasswordResponse,
                                    )
from src.servises.mail import password_reset_email, confirm_email


router = APIRouter(prefix='/auth', tags=["auth"])

security = HTTPBearer()

@router.post("/signup", response_model=UserCreatedResponse, status_code=status.HTTP_201_CREATED)
async def signup(user: UserModel, 
                 background_tasks: BackgroundTasks,
                 request: Request, 
                 db: Session=Depends(get_db)):
    new_user = await UserRepo(db).create_user(user)
    if new_user is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="user is already exists")

    background_tasks.add_task(confirm_email, new_user, request.base_url)
    
    return {"user": new_user}


@router.post("/signin", response_model=TokenModel)
async def signin(request_user: OAuth2PasswordRequestForm=Depends(), db: Session=Depends(get_db)) -> TokenModel:
    user_repo = UserRepo(db)
    cur_user = await user_repo.get_user_by_email(request_user.username)

    if cur_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    
    if not cur_user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="email not confirmed")

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


@router.post("/forgot_password", response_model=PasswordResponse)
async def forgot_password(data: UserMail,
                          background_tasks: BackgroundTasks, 
                          request: Request, 
                          db: Session=Depends(get_db)):
    user = await UserRepo(db).get_user_by_email(data.email)
    if user:
        background_tasks.add_task(password_reset_email, user, request.base_url)
    
    return {}


@router.get("/reset_password/confirm/{token}", response_model=PasswordResponse)
async def forgot_password(token: str,
                          db: Session=Depends(get_db)):
    payload = await auth_token.get_payload(token)

    if payload is None or\
        payload.get("scope") is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")

    user = await UserRepo(db).get_user_by_email(payload.get("sub", ""))
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    
    return {"result": True,
            "detail": "Reset password token is valid"}


@router.post("/reset_password/complete", response_model=PasswordResponse)
async def reset_password(data: ResetPassword, db: Session=Depends(get_db)):
    payload = await auth_token.get_payload(data.token)

    if payload is None or\
        payload.get("scope") is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    
    user_repo = UserRepo(db)
    user = await user_repo.get_user_by_email(payload.get("sub", ""))

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")

    await user_repo.update_password(user, data.password)

    return {"result": True,
            "detail": "Password was successfully reseted"}


@router.get("/confirmed_email/{token}")
async def verify_token(token: str,  db: Session = Depends(get_db)):
    payload = await auth_token.get_payload(token)

    if payload is None or\
        payload.get("scope") is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    
    user_repo = UserRepo(db)
    user = await user_repo.get_user_by_email(payload.get("sub", ""))

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")

    if user.confirmed:
        return {"result": False,
            "detail": "Email is already confirmed"}
    
    await user_repo.confirmed_email(user.email)

    return {"result": True,
            "detail": "Email confirmed"}







    
    

    







    
    
    


