from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Path,
    Query,
    status,
)
from fastapi.responses import PlainTextResponse

from checks import actions
from checks.api.constants import EndpointTag
from checks.api.dependencies.auth import CurrentUserIdDepAnnotated
from checks.api.dependencies.check import get_check_filters
from checks.api.dependencies.db import SessionDepAnnotated
from checks.api.dependencies.pagination import get_page_params
from checks.domain.base import PageParams
from checks.domain.check import Check, CheckCreate, CheckFilters

check_router = APIRouter(prefix="/checks", tags=[EndpointTag.CHECK])


@check_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_description="Created check",
)
async def create_check(
    session: SessionDepAnnotated,
    user_id: CurrentUserIdDepAnnotated,
    check_create: Annotated[CheckCreate, Body()],
) -> Check:
    return await actions.create_check(session, user_id, check_create)


@check_router.get("/")
async def get_checks(
    session: SessionDepAnnotated,
    user_id: CurrentUserIdDepAnnotated,
    check_filters: Annotated[CheckFilters, Depends(get_check_filters)],
    page_params: Annotated[PageParams, Depends(get_page_params)],
) -> tuple[Check, ...]:
    return await actions.get_checks(
        session,
        user_id,
        check_filters,
        page_params,
    )


@check_router.get("/{check_id}")
async def get_check(
    session: SessionDepAnnotated,
    user_id: CurrentUserIdDepAnnotated,
    check_id: Annotated[int, Path(ge=1)],
) -> Check:
    check = await actions.get_check(session, check_id)
    if check.user_id == user_id:
        return check
    raise HTTPException(
        status_code=status.HTTP_402_PAYMENT_REQUIRED,
        detail="Користувач не має доступу до цього чеку.",
    )


@check_router.get("/{check_public_id}/text", response_class=PlainTextResponse)
async def get_check_in_text(
    session: SessionDepAnnotated,
    check_public_id: UUID,
    line_len: Annotated[int, Query(ge=1)] = 30,
) -> str:
    return await actions.get_check_in_text(session, check_public_id, line_len)
