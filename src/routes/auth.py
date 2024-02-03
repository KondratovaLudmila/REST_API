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


from src.dependencies.db import get_db
from src.services.auth import auth_token
from src.services.hash_handler import pwd_handler
from src.repository.users_repo import UserRepo
from src.schemas.user_schema import (UserModel, 
                                    UserCreatedResponse,
                                    TokenModel, 
                                    UserMail, 
                                    ResetPassword, 
                                    PasswordResponse,
                                    )
from src.services.mail import password_reset_email, confirm_email


router = APIRouter(prefix='/auth', tags=["auth"])

security = HTTPBearer()

@router.post("/signup", response_model=UserCreatedResponse, status_code=status.HTTP_201_CREATED)
async def signup(user: UserModel, 
                 background_tasks: BackgroundTasks,
                 request: Request, 
                 db: Session=Depends(get_db)):
    """
    The signup function creates a new user and sends an email to the user's email address.
        The function returns the newly created UserModel object.
    
    
    :param user: UserModel: Get the user data from the request body
    :param background_tasks: BackgroundTasks: Add tasks to the background task queue
    :param request: Request: Get the base_url of the application
    :param db: Session: Get the database session
    :return: A dictionary with a single key, user
    :doc-author: Trelent
    """
    new_user = await UserRepo(db).create_user(user)
    if new_user is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="user is already exists")

    background_tasks.add_task(confirm_email, new_user, request.base_url)
    
    return {"user": new_user}


@router.post("/signin", response_model=TokenModel)
async def signin(request_user: OAuth2PasswordRequestForm=Depends(), db: Session=Depends(get_db)) -> TokenModel:
    """
    The signin function is used to sign in a user.
    It takes the email and password of the user as input, and returns an access token and refresh token
    if successful.
    
    
    :param request_user: OAuth2PasswordRequestForm: Get the username and password from the request body
    :param db: Session: Get the database session
    :return: A tokenmodel object
    :doc-author: Trelent
    """
    user_repo = UserRepo(db)
    cur_user = await user_repo.get_user_by_email(request_user.username)

    if cur_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    
    if not cur_user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")

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
    """
    The refresh_token function is used to refresh the access token.
    It takes in a valid refresh token and returns a new access_token, otherwise raises an HTTPException 401 
    and updated refresh_token pair. The old tokens are invalidated.
    
    :param credentials: HTTPAuthorizationCredentials: Get the authorization header from the request
    :param db: Session: Pass the database session to the function
    :return: A dict that contains the new access_token, refresh_token and token_type
    :doc-author: Trelent
    """
    token = credentials.credentials
    payload = await auth_token.get_payload(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    

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
    """
    The forgot_password function is used to send a password reset email to the user.
    
    The forgot_password function will send an email with a link that allows the user 
    to reset their password. The link expires after 30 minutes. 
    
    :param data: UserMail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: To get the base url of the application
    :param db: Session: Get the database session
    :return: dict with result and detail key
    :doc-author: Trelent
    """
    user = await UserRepo(db).get_user_by_email(data.email)
    if user:
        background_tasks.add_task(password_reset_email, user, request.base_url)
    
    return {"result": True,
            "detail": "We've sent you an email with instructions for password reset"}


@router.get("/reset_password/confirm/{token}", response_model=PasswordResponse)
async def reset_token_validate(token: str,
                          db: Session=Depends(get_db)):
    """
    The reset_token_validate function is used to validate a reset password token.
    It returns {"result": True} if the token is valid, otherwise raises HTTPException code 400.
    
    :param token: str: Get the token from the request body
    :param db: Session: Get the database session
    :return: A dictionary with two keys: result and detail
    :doc-author: Trelent
    """
   
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
    """
    The reset_password function is used to reset a user's password.
    It takes in the ResetPassword data model and returns a dict with the result of the operation.
    If the token is invalid raises HTTPException 400
    
    
    :param data: ResetPassword: Get the token and password from the request body
    :param db: Session: Get the database session
    :return: A dictionary with two keys: result and detail
    :doc-author: Trelent
    """
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
async def confirmed_email(token: str,  db: Session = Depends(get_db)):
    """
    The confirmed_email function confirms the user's email address
    by temporary token sent to user by mail.
    Returns True if the token is valid, and False raises HTTPException code 400.
    
    :param token: str: Get the token from the url
    :param db: Session: Get the database session
    :return: A dictionary with two keys: result and detail
    :doc-author: Trelent
    """
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







    
    

    







    
    
    


