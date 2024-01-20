from jose import jwt, JWTError
from dotenv import load_dotenv, find_dotenv
from os import getenv
from datetime import timedelta, datetime
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status

load_dotenv(find_dotenv())

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/signin")


class AuthToken:
    def __init__(self) -> None:
        self.SECRET_KEY = getenv("REST_API_KEY")
        self.ALGORITHM = getenv("REST_API_ALGORITHM") or "HS256"

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
    
    async def get_payload(self, token: str):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, self.ALGORITHM)
            return payload
        except JWTError:
            return None


auth_token = AuthToken()

