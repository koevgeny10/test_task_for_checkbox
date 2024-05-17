from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import Query
from pydantic.json_schema import SkipJsonSchema

from checks.domain.check import CheckFilters, money_field
from checks.domain.constants import PaymentType

money_query_param = Query(
    ge=0,
    description=money_field.description,
    examples=money_field.examples,
)


async def get_check_filters(
    created_at__ge: Annotated[
        datetime | SkipJsonSchema[None],
        Query(),
    ] = None,
    created_at__le: Annotated[
        datetime | SkipJsonSchema[None],
        Query(),
    ] = None,
    total__ge: Annotated[
        Decimal | SkipJsonSchema[None],
        money_query_param,
    ] = None,
    total__le: Annotated[
        Decimal | SkipJsonSchema[None],
        money_query_param,
    ] = None,
    payment_type__eq: Annotated[
        PaymentType | SkipJsonSchema[None],
        Query(),
    ] = None,
) -> CheckFilters:
    return CheckFilters(
        created_at__ge=created_at__ge,
        created_at__le=created_at__le,
        total__ge=total__ge,
        total__le=total__le,
        payment_type__eq=payment_type__eq,
    )
