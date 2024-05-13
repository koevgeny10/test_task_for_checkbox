# ruff: noqa: ARG001
from sqlalchemy.ext.asyncio import AsyncSession

from checks import repository
from checks.domain.base import PageParams
from checks.domain.check import Check, CheckCreate, CheckFilters
from checks.domain.schemas import UserCreate


async def create_user(session: AsyncSession, user_create: UserCreate) -> None:
    await repository.create_user(session, user_create)


async def create_check(
    session: AsyncSession,
    user_id: int,
    check_create: CheckCreate,
) -> Check:
    return await repository.create_check(session, user_id, check_create)


async def get_check(session: AsyncSession, check_id: int) -> Check:
    return await repository.get_check(session, check_id)


async def get_check_in_text(session: AsyncSession, check_id: int) -> str:
    raise NotImplementedError


async def get_checks(
    session: AsyncSession,
    user_id: int,
    check_filters: CheckFilters | None = None,
    page_params: PageParams | None = None,
) -> tuple[Check, ...]:
    return await repository.get_checks(
        session,
        user_id,
        check_filters,
        page_params,
    )
