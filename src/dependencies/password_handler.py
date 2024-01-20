from passlib.context import CryptContext

class PasswordHandler:
    def __init__(self, schemes: list[str]=["bcrypt"]) -> None:
        self.pwd_context = CryptContext(schemes=schemes, deprecated="auto")

    
    def verify_password(self, plain_password, hashed_password) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    
    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)


pwd_handler = PasswordHandler()