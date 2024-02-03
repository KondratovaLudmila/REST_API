
from sqlalchemy.orm import Session

from src.models.user import User
from src.schemas.user_schema import UserModel, UserUpdatePassword
from src.services.hash_handler import pwd_handler
from src.services.media import MediaCloud



class UserRepo:
    def __init__(self, db: Session):
        """
        The __init__ function is called when the class is instantiated.
        It allows us to set up any attributes that we want to use in the class.
        In this case, we are setting up a database connection (db) and storing it 
        as an attribute of our object.
        
        :param self: Represent the instance of the class
        :param db: Session: Pass in the database session to the class
        :return: An instance of the class
        :doc-author: Trelent
        """
        self.db = db


    async def create_user(self, user: UserModel):
        """
        The create_user function creates a new user in the database.

        :param self: Represent the instance of a class
        :param user: UserModel: Pass in the user object that was created by the usermodel class
        :return: A new User object
        :doc-author: Trelent
        """
        is_unique = await self.get_user_by_email(user.username) == None
        
        if not is_unique:
            return None
        
        new_user = User(email=user.username, password=pwd_handler.get_password_hash(user.password))
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        
        return new_user
    

    async def update_password(self, user: User, password: str) -> User:
        """
        The update_password function updates the password of a user.
        New password is hashing and replace old password in database
        
        :param self: Represent the instance of the class
        :param user: User: Pass in the user object that is being updated
        :param password: str: Get the password from the user and to hash it
        :return: The user object with the new password and a refresh token
        :doc-author: Trelent
        """
        user.password = pwd_handler.get_password_hash(password)
        user.refresh_token = None
        self.db.commit()

        return user            


    async def get_user_by_email(self, email) -> User:
        """
        The get_user_by_email function returns a user object based on the email address provided.
            
        
        :param self: Represent the instance of the class
        :param email: Filter the query to find a user with that email
        :return: The User object which email field matches the given email
        :doc-author: Trelent
        """
        return self.db.query(User).filter(User.email == email).first()
    
    
    async def update_refresh_token(self, user: User, refresh_token: str):
        """
        The update_refresh_token function updates the refresh token for a given user.
        
        :param self: Represent the instance of the class
        :param user: User: Identify the user that is being updated
        :param refresh_token: str: Update the user's refresh token
        :return: The User object with the updated refresh token
        :doc-author: Trelent
        """
        user.refresh_token = refresh_token
        self.db.commit()

        return user


    async def confirmed_email(self, email: str) -> User:
        """
        The confirmed_email function marks a user as confirmed in the database.
        
        :param self: Represent the instance of the class
        :param email: str: Get the email of the user
        :return: The updated User object
        :doc-author: Trelent
        """
        user = await self.get_user_by_email(email)
        if user:
            user.confirmed = True
            self.db.commit()

        return user


    async def update_avatar(self, email, file) -> User:
        """
        The update_avatar function updates the avatar of a user.
        
        :param self: Represent the instance of the class
        :param email: Get the user from the database
        :param file: Upload the avatar to cloudinary
        :return: The updated User object
        :doc-author: Trelent
        """
        user = await self.get_user_by_email(email)
        
        avatar = await MediaCloud().avatar_upload(file, public_id=user.avatar_cld)
        user.avatar = avatar.url
        user.avatar_cld = avatar.public_id
        self.db.commit()

        return user


    