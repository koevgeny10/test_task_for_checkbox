from typing import Any

import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "user_create",
    [
        {
            "name": "Jon",
            "email": "jon@gmail.com",
            "password": "jonjon",
            "password2": "jonjon",
        },
        pytest.param(
            {
                "name": "Jon",
                "email": "jon@gmail.com",
                "password": "jonjon",
                "password2": "qwerty",
            },
            marks=pytest.mark.xfail(reason="Паролі не співпадають"),
        ),
        pytest.param(
            {
                "name": "Jon",
                "email": "jon@gmail.com",
                "password": "q",
                "password2": "q",
            },
            marks=pytest.mark.xfail(reason="Паролі занадто короткі"),
        ),
    ],
)
async def test_create_user(
    client: AsyncClient,
    user_create: dict[str, Any],
) -> None:
    response = await client.post("users/", json=user_create)
    assert response.status_code == 201
