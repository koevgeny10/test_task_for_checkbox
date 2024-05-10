from typing import Annotated

from sqlalchemy import MetaData
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
)


class BaseModel(DeclarativeBase):  # pylint: disable=too-few-public-methods
    metadata = MetaData(
        naming_convention={
            # Именование индексов
            "ix": "ix__%(table_name)s__%(column_0_N_name)s",
            # Именование уникальных индексов
            "uq": "uq__%(table_name)s__%(column_0_N_name)s",
            # Именование CHECK-constraint-ов
            "ck": "ck__%(table_name)s__%(constraint_name)s",
            # Именование внешних ключей
            "fk": (
                "fk__%(table_name)s__%(column_0_N_name)s"
                "__%(referred_table_name)s"
            ),
            # Именование первичных ключей
            "pk": "pk__%(table_name)s",
        },
    )
    __mapper_args__ = {"eager_defaults": True}  # noqa: RUF012

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: N805
        return cls.__name__.lower().replace("model", "s")

    id: Mapped[Annotated[int, mapped_column(primary_key=True, sort_order=-1)]]
