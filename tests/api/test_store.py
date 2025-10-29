import pytest
from httpx import AsyncClient


@pytest.mark.anyio
@pytest.mark.order(3)
async def test_shouldnt_create_store_without_seller(client: AsyncClient):
    request = await client.post(
        "/stores/",
        json={
            "name": "Loja de Teste",
        },
    )
    response = request.json()
    assert request.status_code == 403

@pytest.mark.anyio
@pytest.mark.order(4)
async def test_should_create_store_with_seller(client: AsyncClient):

    # authenticate seller
    request = await client.post(
        "/sellers/auth",
        json={
            "email": "vendedor@magic.com",
            "password": "123456",
        },
    )
    response_seller_authenticated = request.json()
    assert request.status_code == 200
    assert response_seller_authenticated["seller_id"] == 1
    assert response_seller_authenticated["name"] == "Vendedor"
    assert response_seller_authenticated["access_token"] is not None

    # create store
    request = await client.post(
        "/stores/",
        headers={
            "Seller-Authorization": f"Bearer {response_seller_authenticated['access_token']}",
        },
        json={
            "name": "Loja de Teste",
        },
    )
    response_store_created = request.json()
    assert request.status_code == 200
    assert response_store_created["id"] == 1
    assert response_store_created["name"] == "Loja de Teste"