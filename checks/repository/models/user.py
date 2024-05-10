from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.expression import false

from checks.repository.models.base import BaseModel


class UserModel(BaseModel):  # pylint: disable=too-few-public-methods
    name: Mapped[str]
    email: Mapped[str] = mapped_column(
        unique=True,
        index=True,
    )
    is_email_verified: Mapped[bool] = mapped_column(
        server_default=false(),
    )
    hashed_password: Mapped[str]
