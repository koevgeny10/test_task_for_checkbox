# ruff: noqa
# mypy: ignore-errors
# pylint: disable=all
"""
Я взяв цей код з sqlalchemy_utils та адаптував до запуску асинхронно із asyncpg
"""
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy_utils.functions import quote
from sqlalchemy_utils.functions.database import _set_url_database


async def create_database_async(url, encoding="utf8", template=None):
    database = url.database
    url = _set_url_database(url, database="postgres")
    engine = create_async_engine(url, isolation_level="AUTOCOMMIT")
    if not template:
        template = "template1"
    async with engine.begin() as conn:
        text = "CREATE DATABASE {} ENCODING '{}' TEMPLATE {}".format(
            quote(conn, database),
            encoding,
            quote(conn, template),
        )
        await conn.execute(sa.text(text))

    await engine.dispose()


async def drop_database_async(url):
    database = url.database
    url = _set_url_database(url, database="postgres")
    engine = create_async_engine(url, isolation_level="AUTOCOMMIT")
    async with engine.begin() as conn:
        # Disconnect all users from the database we are dropping.
        version = conn.dialect.server_version_info
        pid_column = "pid" if (version >= (9, 2)) else "procpid"
        text = """
        SELECT pg_terminate_backend(pg_stat_activity.{pid_column})
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{database}'
        AND {pid_column} <> pg_backend_pid();
        """.format(
            pid_column=pid_column,
            database=database,
        )
        await conn.execute(sa.text(text))

        # Drop the database.
        text = f"DROP DATABASE {quote(conn, database)}"
        await conn.execute(sa.text(text))

    await engine.dispose()
