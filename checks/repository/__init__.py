from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from checks.domain.base import PageParams
from checks.domain.check import Check, CheckCreate, CheckFilters
from checks.domain.schemas import UserCreate
from checks.repository.models.check import CheckModel
from checks.repository.models.user import UserModel
from checks.repository.queries import (
    get_select_check_by_public_id_sql_query,
    get_select_checks_sql_query,
    get_select_user_filtered_by_email_sql_query,
)


async def create_user(session: AsyncSession, user_create: UserCreate) -> None:
    user = UserModel(**user_create.model_dump())
    async with session.begin():
        session.add(user)


async def get_user_by_email(
    session: AsyncSession,
    email: str,
) -> UserModel | None:
    return (
        await session.execute(
            get_select_user_filtered_by_email_sql_query(email),
        )
    ).scalar()


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


async def get_check_by_public_id(
    session: AsyncSession,
    check_public_id: UUID,
) -> Check:
    return Check.model_validate(
        (
            await session.execute(
                get_select_check_by_public_id_sql_query(check_public_id),
            )
        ).scalar_one(),
    )


async def get_checks(
    session: AsyncSession,
    user_id: int,
    check_filters: CheckFilters | None = None,
    page_params: PageParams | None = None,
) -> tuple[Check, ...]:
    return tuple(
        Check.model_validate(check)
        for check in await session.scalars(
            get_select_checks_sql_query(user_id, check_filters, page_params),
        )
    )
