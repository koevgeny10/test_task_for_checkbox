from collections.abc import AsyncGenerator, Generator
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from functools import partial
from typing import Literal
from uuid import uuid4

import pytest
from _pytest.monkeypatch import MonkeyPatch
from alembic.command import downgrade, upgrade
from httpx import AsyncClient
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from checks.api import app
from checks.api.dependencies.db import (
    get_session_from_factory,
    get_session_from_factory_dependency,
)
from checks.repository.connect import (
    get_db_url,
    get_sa_engine,
    get_sa_sessionmaker,
)
from tests.constants import alembic_config
from tests.databases_menagment import (
    create_database_async,
    drop_database_async,
)


@pytest.fixture(name="anyio_backend", autouse=True)
def anyio_backend_fixture() -> (
    tuple[Literal["asyncio"], dict[Literal["use_uvloop"], Literal[True]]]
):
    """Для настройки бекенда anyio для тестов."""
    return "asyncio", {"use_uvloop": True}


@pytest.fixture(autouse=True)
def _mock_env_postgres_db(monkeypatch: MonkeyPatch) -> None:
    """Мокает имя базы данных.

    Для того, что бы alembic создал правильную ссылку и выполнил миграции.
    """
    temp_db_name = f"{uuid4().hex}_pytest"
    monkeypatch.setenv("POSTGRES_DB", temp_db_name)


@pytest.fixture(name="db_url")
async def db_url_fixture() -> AsyncGenerator[URL, None]:
    db_url = get_db_url()
    await create_database_async(db_url)  # type: ignore[no-untyped-call]
    yield db_url
    await drop_database_async(db_url)  # type: ignore[no-untyped-call]


@pytest.fixture(name="alembic_engine")
async def alembic_engine_fixture(
    db_url: URL,
) -> AsyncGenerator[AsyncEngine, None]:
    """Нужно также для тестов из модуля pytest-alembic."""
    engine = get_sa_engine(db_url)
    yield engine
    await engine.dispose()


@contextmanager
def _migrations() -> Generator[None, None, None]:
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(upgrade, alembic_config, "head").result()
        yield
        executor.submit(downgrade, alembic_config, "base").result()


@pytest.fixture(name="session_getter")
async def session_getter_fixture(
    alembic_engine: AsyncEngine,
) -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    with _migrations():
        session_getter = get_sa_sessionmaker(alembic_engine)
        yield session_getter


@pytest.fixture(name="session")
async def session_fixture(
    session_getter: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    async with session_getter() as session:
        yield session


@contextmanager
def _override_dependency(
    session_getter: async_sessionmaker[AsyncSession],
) -> Generator[None, None, None]:
    override_get_session = partial(
        get_session_from_factory,
        session_getter,
    )
    app.dependency_overrides[get_session_from_factory_dependency] = (
        override_get_session
    )
    yield
    app.dependency_overrides = {}


@pytest.fixture(name="client")
async def client_fixture(
    session_getter: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncClient, None]:
    with _override_dependency(session_getter):
        async with AsyncClient(app=app, base_url="http://tests") as client:
            yield client
