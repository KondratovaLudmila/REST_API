from jose import jwt, JWTError
from dotenv import load_dotenv, find_dotenv
from os import getenv
from datetime import timedelta, datetime
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status


from ..conf.config import settings
from src.repository.users_repo import UserRepo


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/signin")


class AuthToken:
    def __init__(self) -> None:
        self.SECRET_KEY = settings.secret_key
        self.ALGORITHM = settings.algorithm or "HS256"


    async def create_access_token(self, data: dict, life_time: timedelta=timedelta(minutes=15)):

        payload = data.copy()
        payload.update({
                        "iat": datetime.utcnow(),
                        "exp": datetime.utcnow() + life_time,
                        "scope": "access_token"
                        })
        token = jwt.encode(payload, self.SECRET_KEY, self.ALGORITHM)

        return token
    

    async def create_refresh_token(self, data: dict, life_time: timedelta=timedelta(days=1)):

        payload = data.copy()
        payload.update({
                        "iat": datetime.utcnow(),
                        "exp": datetime.utcnow() + life_time,
                        "scope": "refresh_token"
                        })
        refresh_token = jwt.encode(payload, self.SECRET_KEY, self.ALGORITHM)

        return refresh_token
    
    
    async def create_token(self, data: dict, life_time: timedelta=timedelta(days=3)):
        payload = data.copy()
        expire = datetime.utcnow() + life_time
        payload.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)
        
        return token
    

    async def get_payload(self, token: str):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, self.ALGORITHM)
            return payload
        except JWTError:
            return None


auth_token = AuthToken()

