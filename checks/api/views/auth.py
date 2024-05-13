from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from jose import jwt

from checks.api.constants import EndpointTag
from checks.api.dependencies.auth import get_user_auth_data
from checks.api.schemas import UserAuthData
from checks.api.settings import (
    JWT_LIFETIME,
    JWT_PRIVATE_KEY,
    JWT_SIGNING_ALGORITHM,
)

auth_router = APIRouter(prefix="/auth", tags=[EndpointTag.AUTH])


@auth_router.post("/bearer_token", response_description="Bearer token")
async def get_bearer_token(
    user_auth_data: Annotated[UserAuthData, Depends(get_user_auth_data)],
) -> str:
    """Для получения Bearer token."""
    jwt_deadline = datetime.now(tz=UTC) + JWT_LIFETIME
    jwt_unsigned = {
        "sub": user_auth_data.model_dump_json(),
        "exp": jwt_deadline,
    }
    return jwt.encode(
        jwt_unsigned,
        JWT_PRIVATE_KEY,
        algorithm=JWT_SIGNING_ALGORITHM,
    )
