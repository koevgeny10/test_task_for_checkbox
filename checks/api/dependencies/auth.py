from typing import Annotated

from fastapi import Body, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import ValidationError

from checks.api.dependencies.db import SessionDepAnnotated
from checks.api.schemas import Credentials, UserAuthData
from checks.api.settings import JWT_PUBLIC_KEY, JWT_SIGNING_ALGORITHM
from checks.domain.constants import PWD_CONTEXT
from checks.repository import get_user_by_email


async def get_user_auth_data(
    session: SessionDepAnnotated,
    credentials: Annotated[Credentials, Body()],
) -> UserAuthData:
    """Находит пользователя по credentials."""
    user = await get_user_by_email(session, credentials.email)
    if user is not None and PWD_CONTEXT.verify(
        credentials.password.get_secret_value(),
        user.hashed_password,
    ):
        return UserAuthData.model_validate(user)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_auth_data_of_active_user(
    token: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
) -> UserAuthData:
    try:
        user_auth_data = UserAuthData.model_validate_json(
            jwt.decode(
                token.credentials,
                JWT_PUBLIC_KEY,
                algorithms=JWT_SIGNING_ALGORITHM,
            )["sub"],
        )
    except (JWTError, KeyError, ValidationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    if user_auth_data.is_active:
        return user_auth_data
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Inactive user",
    )


async def get_current_user_id(
    current_user_auth_data: Annotated[
        UserAuthData,
        Depends(get_auth_data_of_active_user),
    ],
) -> int:
    return current_user_auth_data.id


CurrentUserIdDepAnnotated = Annotated[int, Depends(get_current_user_id)]
