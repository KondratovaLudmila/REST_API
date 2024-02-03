from typing import Any
import unittest
from unittest.mock import patch, Mock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.user import User, Base
from src.schemas.user_schema import UserModel
from src.repository.users_repo import UserRepo
from src.services.hash_handler import pwd_handler
from src.services.media import MediaCloud
import os
import dotenv

dotenv.load_dotenv()

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
port = os.getenv("POSTGRES_PORT")
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@localhost:{port}/tests"

print(SQLALCHEMY_DATABASE_URL)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def eq_users(usr1: User, usr2: User, msg=None):
    result = usr1.email == usr2.email and\
            usr1.password == usr2.password and\
            usr1.confirmed == usr2.confirmed and\
            usr1.refresh_token == usr2.refresh_token and\
            usr1.avatar == usr2.avatar and\
            usr1.avatar_cld == usr2.avatar_cld
    
    return result


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.session = TestingSessionLocal()

        #Add users
        user1 = User(email="user@i.ua", 
                     password="123",
                     refresh_token="777",
                     avatar="www.123/5678hhh.jpeg",
                     avatar_cld="5678hhh",
                     confirmed=False
                     )
        user2 = User(email="user2@i.ua", 
                     password="111",
                     refresh_token="999",
                     confirmed=True
                     )
        self.session.add(user1)
        self.session.add(user2)
        self.session.commit()

        self.users = [user1, user2]

        self.addTypeEqualityFunc(User, eq_users)


    def tearDown(self) -> None:
        self.session.close()
        

    async def test_create_user(self):
        user = UserModel(username="user3@i.ua", 
                        password="555"
                        )
        
        with patch.object(pwd_handler, "get_password_hash", return_value=password) as hash_mock:
            result = await UserRepo(db=self.session).create_user(user)

            self.assertEqual(result, User(email=user.username, password=user.password))
            hash_mock.assert_called_once_with(user.password)


    async def test_create_user_duplicate(self):
        user = UserModel(username="user2@i.ua", 
                        password="111"
                        )
        
        result = await UserRepo(db=self.session).create_user(user)

        self.assertIsNone(result)

    
    async def test_update_password(self):
        user = self.users[1]
        password = "000"
        with patch.object(pwd_handler, "get_password_hash", return_value=password) as hash_mock:
            result = await UserRepo(db=self.session).update_password(user=user, password=password)

            self.assertEqual(result.password, password)
            hash_mock.assert_called_once_with(password)

        

    async def test_get_user_by_email_found(self):
        user = self.users[1]

        result = await UserRepo(db=self.session).get_user_by_email(user.email)

        self.assertEqual(result, user)


    async def test_get_user_by_email_not_found(self):

        result = await UserRepo(db=self.session).get_user_by_email("test@i.ua")

        self.assertIsNone(result)


    async def test_update_refresh_token(self):
        user = self.users[1]
        old_token = user.refresh_token

        result = await UserRepo(db=self.session).update_refresh_token(user, "ddd")

        self.assertEqual(result, user)
        self.assertNotEqual(result.refresh_token, old_token)


    async def test_confirm_email(self):
        user = self.users[0]

        result = await UserRepo(db=self.session).confirmed_email(user.email)

        self.assertEqual(result, user)
        self.assertTrue(result.confirmed)


    async def test_confirm_email_wrong_email(self):
        email = "test@test.ua"
        result = await UserRepo(db=self.session).confirmed_email(email)

        self.assertIsNone(result)


    async def test_update_avatar(self):
        user = self.users[0]
        file = None
        url = "www.test/76576kljlkjlk.jpeg"
        public_id = "76576kljlkjlk"
        with patch.object(MediaCloud, "avatar_upload", return_value=Mock(url=url, public_id=public_id)):
            result = await UserRepo(db=self.session).update_avatar(user.email, file)

        self.assertEqual(result.avatar, url)
        self.assertEqual(result.avatar_cld, public_id)


if __name__ == '__main__':
    unittest.main()
