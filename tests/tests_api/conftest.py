from collections.abc import Generator
from datetime import UTC, datetime

import pytest
from httpx import AsyncClient, Auth, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from checks.api.schemas import UserAuthData
from checks.api.views.auth import get_bearer_token
from checks.domain.constants import PWD_CONTEXT
from checks.repository.models import CheckModel, UserModel


@pytest.fixture(name="user")
async def save_user(session: AsyncSession) -> UserModel:
    user = UserModel(
        name="Jon",
        email="jon@gmail.com",
        hashed_password=PWD_CONTEXT.hash("jonjon"),
    )
    async with session.begin():
        session.add(user)
    return user


class BearerAuth(Auth):
    def __init__(self, token: str):
        self.token = token

    def auth_flow(
        self,
        request: Request,
    ) -> Generator[Request, Response, None]:
        # Send the request, with a custom `Authorization` header.
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request


@pytest.fixture()
async def registered_client(
    client: AsyncClient,
    user: UserModel,
) -> AsyncClient:
    bearer_token = await get_bearer_token(
        UserAuthData(
            email=user.email,
            name=user.name,
            id=user.id,
            is_active=user.is_active,
        ),
    )
    client.auth = BearerAuth(bearer_token)
    return client


@pytest.fixture(name="save_checks")
async def _save_checks(session: AsyncSession, user: UserModel) -> None:
    async with session.begin():
        session.add_all(
            [
                CheckModel(
                    public_id="fb8c829a-4a4e-4703-b77a-a5980def7647",
                    user_id=user.id,
                    products=[
                        {
                            "name": "Футболка",
                            "price": "199.99",
                            "quantity": 3,
                        },
                        {
                            "name": "Джинси",
                            "price": "1000.54",
                            "quantity": 2,
                        },
                    ],
                    total="2601.05",
                    payment={
                        "type": "cash",
                        "amount": "3000",
                    },
                    created_at=datetime(2020, 1, 2, 3, 4, 5, tzinfo=UTC),
                ),
                CheckModel(
                    user_id=user.id,
                    products=[
                        {
                            "name": "Шоколадка",
                            "price": "50.11",
                            "quantity": 3,
                        },
                        {
                            "name": "Булочка",
                            "price": "20.22",
                            "quantity": 2,
                        },
                    ],
                    total="190.77",
                    payment={
                        "type": "cashless",
                        "amount": "300",
                    },
                    created_at=datetime(2021, 2, 3, 4, 5, 6, tzinfo=UTC),
                ),
                CheckModel(
                    user_id=user.id,
                    products=[
                        {
                            "name": "Рушник",
                            "price": "200.99",
                            "quantity": 1,
                        },
                        {
                            "name": "Шампунь",
                            "price": "150.71",
                            "quantity": 3,
                        },
                    ],
                    total="653.12",
                    payment={
                        "type": "cash",
                        "amount": "800",
                    },
                    created_at=datetime(2022, 3, 4, 5, 6, 7, tzinfo=UTC),
                ),
                CheckModel(
                    user_id=user.id,
                    products=[
                        {
                            "name": "Піца",
                            "price": "250.63",
                            "quantity": 1,
                        },
                        {
                            "name": "Ковбаса",
                            "price": "203.28",
                            "quantity": 2,
                        },
                        {
                            "name": "Сир",
                            "price": "162.85",
                            "quantity": 3,
                        },
                        {
                            "name": "Хліб",
                            "price": "40.39",
                            "quantity": 2,
                        },
                    ],
                    total="1226.52",
                    payment={
                        "type": "cashless",
                        "amount": "1500",
                    },
                    created_at=datetime(2023, 4, 5, 6, 7, 8, tzinfo=UTC),
                ),
            ],
        )
