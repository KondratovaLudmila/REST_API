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
        """
        The __init__ function is called when the class is instantiated.
        It sets up the instance of the class with a secret key and an algorithm.
        The secret key should be set to settings.secret_key, which will be imported from settings.py.
        
        :param self: Represent the instance of the class
        :return: None
        :doc-author: Trelent
        """
        self.SECRET_KEY = settings.secret_key
        self.ALGORITHM = settings.algorithm or "HS256"


    async def create_access_token(self, data: dict, life_time: timedelta=timedelta(minutes=15)):
        """
        The create_access_token function creates a JWT token with the given payload.
        The function takes in a dictionary of data, and an optional life_time argument.
        The data is a dictionary that can contain any key-value pairs.

        
        :param self: Represent the instance of the class
        :param data: dict: Pass the data that will be encoded in the jwt
        :param life_time: timedelta: Set the life time of the token. default life time is 15 minutes.
        :return: The JWT token in bytes
        :doc-author: Trelent
        """

        payload = data.copy()
        payload.update({
                        "iat": datetime.utcnow(),
                        "exp": datetime.utcnow() + life_time,
                        "scope": "access_token"
                        })
        token = jwt.encode(payload, self.SECRET_KEY, self.ALGORITHM)

        return token
    

    async def create_refresh_token(self, data: dict, life_time: timedelta=timedelta(days=1)):
        """
        The create_refresh_token function creates a refresh token for the user.
        The function takes in a dictionary of data, and an optional life_time argument.
        
        :param self: Represent the instance of the class
        :param data: dict: Pass the data that will be encoded in the token
        :param life_time: timedelta: Set the time for which the token will be valid The default life time is 1 day (24 hours). 
        :return: The JWT token in bytes
        :doc-author: Trelent
        """
        
        payload = data.copy()
        payload.update({
                        "iat": datetime.utcnow(),
                        "exp": datetime.utcnow() + life_time,
                        "scope": "refresh_token"
                        })
        refresh_token = jwt.encode(payload, self.SECRET_KEY, self.ALGORITHM)

        return refresh_token
    
    
    async def create_token(self, data: dict, life_time: timedelta=timedelta(days=3)):
        """
        The create_token function creates a custom JWT token with the given payload and life_time.
        
        
        :param self: Represent the instance of the class
        :param data: dict: Pass the data that will be encoded into the token
        :param life_time: timedelta: Set the time that the token will expire. The default life_time is 3 days.
        :return: The JWT token in bytes
        :doc-author: Trelent
        """
        
        payload = data.copy()
        expire = datetime.utcnow() + life_time
        payload.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)
        
        return token
    

    async def get_payload(self, token: str):
        """
        The get_payload function takes a JWT token as an argument and returns the payload of that token.
        If the token is invalid, it will return None.
        
        :param self: Represent the instance of the class
        :param token: str: Pass in the token that is being decoded
        :return: A dictionary of the payload
        :doc-author: Trelent
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, self.ALGORITHM)
            return payload
        except JWTError:
            return None


auth_token = AuthToken()

