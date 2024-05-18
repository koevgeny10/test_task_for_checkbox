from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, status
from sqlalchemy.exc import IntegrityError

from checks import actions
from checks.api.constants import EndpointTag
from checks.api.dependencies.db import SessionDepAnnotated
from checks.domain.user import UserCreate

users_router = APIRouter(prefix="/users", tags=[EndpointTag.USER])


@users_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    session: SessionDepAnnotated,
    user_create: Annotated[UserCreate, Body()],
) -> None:
    """Створення користувачів."""
    try:
        await actions.create_user(session, user_create)
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Цей email зайнятий",
        ) from e
