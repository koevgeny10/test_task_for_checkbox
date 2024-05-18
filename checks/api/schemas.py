from checks.domain.base import IdSchema
from checks.domain.user import Password, UserBase, UserEmail


class Credentials(UserEmail):
    password: Password


class UserAuthData(IdSchema, UserBase):
    is_active: bool
