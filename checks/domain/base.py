from typing import TypedDict

from pydantic import BaseModel, PositiveInt


class IdSchema(BaseModel, from_attributes=True):
    id: PositiveInt


class PageParams(TypedDict):
    offset: int | None
    limit: int
