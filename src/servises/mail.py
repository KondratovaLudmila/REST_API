from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pathlib import Path
from collections.abc import Coroutine
from functools import wraps


from src.conf.config import settings
from src.models.user import User
from src.servises.auth import auth_token

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail.username,
    MAIL_PASSWORD=settings.mail.password,
    MAIL_FROM=settings.mail.mail_from,
    MAIL_PORT=settings.mail.port,
    MAIL_SERVER=settings.mail.server,
    MAIL_FROM_NAME=settings.mail.mail_from,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent.joinpath('templates'),
)

def error_handler(func: callable) -> Coroutine:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
        except ConnectionErrors as err:
            print(err)
        
        return result
    
    return wrapper


@error_handler
async def password_reset_email(user: User, host: str):
    token = await auth_token.create_token({"sub": user.email})
    print(token)
    message = MessageSchema(
        subject="Reset password",
        recipients=[user.email],
        template_body={"host": host, "token": token},
        subtype=MessageType.html
    )
    
    fm = FastMail(conf)
    await fm.send_message(message, template_name="password_reset_email.html")


@error_handler
async def confirm_email(user: User, host: str):
    token = await auth_token.create_token({"sub": user.email})
    message = MessageSchema(
        subject="Email confirmation",
        recipients=[user.email],
        template_body={"host": host, "token": token},
        subtype=MessageType.html
    )


    fm = FastMail(conf)
    await fm.send_message(message, template_name="password_confirm_email.html")
