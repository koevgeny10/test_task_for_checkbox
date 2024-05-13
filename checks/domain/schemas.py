from functools import cached_property
from typing import Annotated, Self

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    SecretStr,
    computed_field,
    model_validator,
)

from checks.domain.constants import PWD_CONTEXT

Password = Annotated[SecretStr, Field(min_length=6)]


class UserEmail(BaseModel):
    email: EmailStr


class UserBase(UserEmail):
    name: str


_PasswordForCheck = Annotated[Password, Field(exclude=True)]


class UserCreate(UserBase):
    password: _PasswordForCheck
    password2: _PasswordForCheck

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        pw1 = self.password
        pw2 = self.password2
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError("passwords don't match")
        return self

    @computed_field  # type: ignore[misc]
    @cached_property
    def hashed_password(self) -> str:
        return PWD_CONTEXT.hash(self.password.get_secret_value())
