from functools import partial
from textwrap import wrap
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from checks import repository
from checks.domain.base import PageParams
from checks.domain.check import Check, CheckCreate, CheckFilters
from checks.domain.constants import PaymentType
from checks.domain.schemas import UserCreate
from checks.repository import get_check_by_public_id


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


async def get_check_in_text(
    session: AsyncSession,
    check_public_id: UUID,
    line_len: int = 30,
) -> str:
    check = await get_check_by_public_id(session, check_public_id)

    _wrap = partial(wrap, width=line_len)

    return f"\n{"=" * line_len}\n".join(
        (
            "\n".join(_wrap("ФОП Джонсонюк Борис")),
            f"\n{"-" * line_len}\n".join(
                "\n".join(
                    (
                        "\n".join(
                            _wrap(f"{product.quantity} x {product.price}"),
                        ),
                        "\n".join(_wrap(product.name)),
                        str(product.total),
                    ),
                )
                for product in check.products
            ),
            "\n".join(
                (
                    f"СУМА {check.total}",
                    (
                        f"{
                            "ГОТІВКА"
                            if check.payment.type == PaymentType.CASH
                            else "КАРТКА"
                        }"
                        f" {check.payment.amount}"
                    ),
                    f"РЕШТА {check.rest}",
                ),
            ),
            "\n".join(
                (
                    str(check.created_at),
                    "Дякуємо за покупку!",
                ),
            ),
        ),
    )


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
