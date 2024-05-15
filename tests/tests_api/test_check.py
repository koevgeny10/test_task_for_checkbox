from datetime import UTC, datetime
from typing import Any

import pytest
from httpx import AsyncClient
from httpx._types import QueryParamTypes


@pytest.mark.parametrize(
    "check_create",
    [
        {
            "products": [
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
            "payment": {
                "type": "cash",
                "amount": "3000",
            },
        },
        pytest.param(
            {
                "products": [
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
                "payment": {
                    "type": "cash",
                    "amount": "11.11",
                },
            },
            marks=pytest.mark.xfail(reason="Недостатня оплата"),
        ),
        pytest.param(
            {
                "products": [],
                "payment": {
                    "type": "cash",
                    "amount": "3000",
                },
            },
            marks=pytest.mark.xfail(reason="Немає товарів"),
        ),
        pytest.param(
            {
                "products": [
                    {
                        "name": "Футболка",
                        "price": "-199.99",
                        "quantity": 3,
                    },
                    {
                        "name": "Джинси",
                        "price": "-1000.54",
                        "quantity": 2,
                    },
                ],
                "payment": {
                    "type": "cash",
                    "amount": "-3000",
                },
            },
            marks=pytest.mark.xfail(reason="Від'ємна кількість грошей"),
        ),
    ],
)
async def test_create_check(
    registered_client: AsyncClient,
    check_create: dict[str, Any],
) -> None:
    response = await registered_client.post("checks/", json=check_create)
    assert response.status_code == 201

    check = response.json()
    products = check["products"]
    assert products[0]["total"] == "599.97"
    assert products[1]["total"] == "2001.08"
    assert check["total"] == "2601.05"
    assert check["rest"] == "398.95"


@pytest.mark.usefixtures("save_checks")
@pytest.mark.parametrize(
    ("params", "expected_check_ids"),
    [
        ({"created_at__ge": str(datetime(2022, 1, 1, tzinfo=UTC))}, (3, 4)),
        ({"total__le": 1000}, (2, 3)),
        ({"offset": 1, "limit": 2}, (2, 3)),
    ],
)
async def test_get_checks(
    registered_client: AsyncClient,
    params: QueryParamTypes,
    expected_check_ids: tuple[int, ...],
) -> None:
    response = await registered_client.get("checks/", params=params)
    assert response.status_code == 200
    assert (
        tuple(check["id"] for check in response.json()) == expected_check_ids
    )


@pytest.mark.usefixtures("save_checks")
async def test_get_check(registered_client: AsyncClient) -> None:
    response = await registered_client.get("checks/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

    response = await registered_client.get("checks/3")
    assert response.status_code == 200
    assert response.json()["id"] == 3
