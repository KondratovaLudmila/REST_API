
from sqlalchemy.orm import Session

from src.models.user import User
from src.schemas.user_schema import UserModel, UserUpdatePassword
from src.servises.password_handler import pwd_handler



class UserRepo:
    def __init__(self, db: Session):
        self.db = db


    async def create_user(self, user: UserModel):
        is_unique = await self.get_user_by_email(user.username) == None
        
        if not is_unique:
            return None
        
        new_user = User(email=user.username, password=pwd_handler.get_password_hash(user.password))
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        return new_user
    

    async def update_password(self, pk: int, pwd: UserUpdatePassword) -> User:
        user = await self.get_user(pk)
        if not pwd_handler.verify_password(pwd.curr_password, user.password):
            return None
        
        user.password = pwd_handler.get_password_hash(pwd.curr_password)
        self.db.commit()

        return user            


    async def get_user_by_email(self, email) -> User:
        return self.db.query(User).filter(User.email == email).first()
    
    
    async def update_refresh_token(self, user: User, refresh_token: str):
        user.refresh_token = refresh_token
        self.db.commit()
