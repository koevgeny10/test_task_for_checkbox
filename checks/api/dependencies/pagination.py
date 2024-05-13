from typing import Annotated

from fastapi import Query

from checks.domain.base import PageParams


async def get_page_params(
    offset: Annotated[
        int,
        Query(
            ge=0,
            title="Отступ",
            description="Для пагинации. Сколько объектов пропустить c начала?",
        ),
    ] = 0,
    limit: Annotated[
        int | None,
        Query(
            ge=0,
            title="Лимит",
            description="Для пагинации. Сколько объектов выбрать?",
        ),
    ] = None,
) -> PageParams:
    return PageParams(offset=offset, limit=limit)
