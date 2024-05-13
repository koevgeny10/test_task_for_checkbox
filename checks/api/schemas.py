from checks.domain.base import IdSchema
from checks.domain.schemas import Password, UserBase, UserEmail


class Credentials(UserEmail):
    password: Password


class UserAuthData(IdSchema, UserBase):
    is_active: bool
