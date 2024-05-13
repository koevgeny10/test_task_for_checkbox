from typing import Annotated

from fastapi import APIRouter, Body, status

from checks import actions
from checks.api.constants import EndpointTag
from checks.api.dependencies.db import SessionDepAnnotated
from checks.domain.schemas import UserCreate

users_router = APIRouter(prefix="/users", tags=[EndpointTag.USER])


@users_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    session: SessionDepAnnotated,
    user_create: Annotated[UserCreate, Body()],
) -> None:
    """Створення користувачів."""
    await actions.create_user(session, user_create)
