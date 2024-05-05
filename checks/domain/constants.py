from passlib.context import CryptContext

PASSWORD_MIN_LENGTH = 6
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
