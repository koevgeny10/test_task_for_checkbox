from collections.abc import Mapping
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from checks.domain.check import Check, CheckCreate
from checks.domain.user import UserCreate
from checks.repository.models.check import CheckModel
from checks.repository.models.user import UserModel
from checks.repository.queries import get_select_checks_sql_query


async def create_user(session: AsyncSession, user_create: UserCreate) -> None:
    user = UserModel(**user_create.model_dump())
    async with session.begin():
        session.add(user)


async def create_check(
    session: AsyncSession,
    user_id: int,
    check_create: CheckCreate,
) -> Check:
    check = CheckModel(user_id=user_id, **check_create.model_dump())
    async with session.begin():
        session.add(check)
    return Check.model_validate(check)


async def get_check(session: AsyncSession, check_id: int) -> Check:
    return Check.model_validate(await session.get_one(CheckModel, check_id))


async def get_checks(
    session: AsyncSession,
    user_id: int,
    filters: Mapping[str, Any],
) -> tuple[Check, ...]:
    return tuple(
        Check.model_validate(check)
        for check in await session.scalars(
            get_select_checks_sql_query(user_id, filters),
        )
    )
