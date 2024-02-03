from passlib.context import CryptContext

class PasswordHandler:
    def __init__(self, schemes: list[str]=["bcrypt"]) -> None:
        """
        The __init__ function initializes the class with a list of schemes.
        The default is bcrypt, but you can add more if you want to use other hashing algorithms.
        
        :param self: Represent the instance of the class
        :param schemes: list[str]: Specify the hashing algorithms to be used by the cryptcontext class
        :return: None
        :doc-author: Trelent
        """
        self.pwd_context = CryptContext(schemes=schemes, deprecated="auto")

    
    def verify_password(self, plain_password, hashed_password) -> bool:
        """
        The verify_password function takes a plain-text password and the hashed version of that password,
        hashes plain password and check if they match each other
        Returns True if they match, False otherwise.
        
        
        :param self: Represent the instance of the class
        :param plain_password: Verify the password entered by the user
        :param hashed_password: Check if the password is correct
        :return: A boolean value
        :doc-author: Trelent
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    
    def get_password_hash(self, password: str) -> str:
        """
        The get_password_hash function takes a password as input and returns the hash of that password.
        The function uses the pwd_context object to generate a hash from the given password.
        
        :param self: Represent the instance of the class
        :param password: str: Pass in the password that is going to be hashed
        :return: A string of the hashed password
        :doc-author: Trelent
        """
        return self.pwd_context.hash(password)


pwd_handler = PasswordHandler()