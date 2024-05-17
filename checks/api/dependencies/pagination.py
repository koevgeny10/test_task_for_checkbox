from typing import Annotated

from fastapi import Query
from pydantic.json_schema import SkipJsonSchema

from checks.domain.base import PageParams


async def get_page_params(
    offset: Annotated[
        int | SkipJsonSchema[None],
        Query(
            ge=0,
            title="Отступ",
            description="Для пагинации. Сколько объектов пропустить c начала?",
        ),
    ] = None,
    limit: Annotated[
        int,
        Query(
            ge=0,
            le=50,
            title="Лимит",
            description="Для пагинации. Сколько объектов выбрать?",
        ),
    ] = 50,
) -> PageParams:
    return PageParams(offset=offset, limit=limit)
