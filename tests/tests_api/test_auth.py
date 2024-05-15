import pytest
from httpx import AsyncClient


@pytest.mark.usefixtures("user")
async def test_get_bearer_token(client: AsyncClient) -> None:
    credentials = {
        "email": "jon@gmail.com",
        "password": "jonjon",
    }
    response = await client.post("auth/bearer_token", json=credentials)
    assert response.status_code == 200
    assert len(response.text) > 0
