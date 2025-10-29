import pytest
from httpx import AsyncClient


@pytest.mark.anyio
@pytest.mark.order(1)
async def test_should_create_customer(client: AsyncClient):
    request = await client.post(
        "/customers/",
        json={
            "name": "Guilherme",
            "email": "guilherme@gmail.com",
            "password": "123456",
        },
    )
    response = request.json()
    assert request.status_code == 200
    assert response["customer_id"] == 1
    assert response["name"] == "Guilherme"
    assert response["access_token"] is not None