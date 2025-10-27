import pytest
from httpx import AsyncClient


@pytest.mark.anyio
@pytest.mark.order(1)
async def test_should_create_store(client: AsyncClient):
    request = await client.post(
        "/stores/",
        json={
            "name": "Guilherme",
            "email": "guilherme@obscure.network",
        },
    )
    response = request.json()
    assert request.status_code == 200
    assert response["id"] == 1
    assert response["name"] == "Guilherme"