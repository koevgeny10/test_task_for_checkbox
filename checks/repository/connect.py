"""Для з'єднання з базою данних."""

from functools import partial
from os import getenv

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)


def get_db_url() -> URL:
    return URL.create(
        drivername="postgresql+asyncpg",
        username=getenv("POSTGRES_USER"),
        password=getenv("POSTGRES_PASSWORD"),
        host=getenv("POSTGRES_HOST"),
        port=int(getenv("POSTGRES_PORT", "5432")),
        database=getenv("POSTGRES_DB"),
    )


get_sa_engine = partial(create_async_engine)
get_sa_sessionmaker = partial(async_sessionmaker, expire_on_commit=False)

sa_session_getter = get_sa_sessionmaker(bind=get_sa_engine(get_db_url()))
