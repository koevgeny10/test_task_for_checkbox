from enum import StrEnum, auto, unique

from passlib.context import CryptContext

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


@unique
class PaymentType(StrEnum):
    CASH = auto()
    CASHLESS = auto()
