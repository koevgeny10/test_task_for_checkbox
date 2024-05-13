from collections.abc import AsyncGenerator
from functools import partial
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from checks.repository.connect import sa_session_getter


async def get_session_from_factory(
    session_factory: async_sessionmaker[AsyncSession] = sa_session_getter,
) -> AsyncGenerator[AsyncSession, None]:
    session = session_factory()
    try:
        yield session
    finally:
        await session.close()


get_session_from_factory_dependency = partial(
    get_session_from_factory,
    sa_session_getter,
)
SessionDepAnnotated = Annotated[
    AsyncSession,
    Depends(get_session_from_factory_dependency),
]
