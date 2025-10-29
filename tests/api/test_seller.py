import pytest
from httpx import AsyncClient


@pytest.mark.anyio
@pytest.mark.order(2)
async def test_should_create_seller(client: AsyncClient):
    request = await client.post(
        "/sellers/",
        json={
            "name": "Vendedor",
            "email": "vendedor@magic.com",
            "password": "123456",
        },
    )
    response = request.json()
    assert request.status_code == 200
    assert response["seller_id"] == 1
    assert response["name"] == "Vendedor"
    assert response["access_token"] is not None