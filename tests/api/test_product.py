import pytest
from httpx import AsyncClient


@pytest.mark.anyio
@pytest.mark.order(7)
async def test_shouldnt_create_product_without_seller_authorization(client: AsyncClient):
    request = await client.post(
        "/stores/1/products",
        json={
            "name": "Produto de Teste",
            "description": "Descrição do produto de teste",
            "price": 100,
            "external_id": "1234567890",
        },
    )
    response = request.json()
    assert request.status_code == 403

@pytest.mark.anyio
@pytest.mark.order(7)
async def test_shouldnt_create_product_without_store(client: AsyncClient):

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

    # create product
    request = await client.post(
        "/stores/2/products",
        headers={
            "Seller-Authorization": f"Bearer {response_seller_authenticated['access_token']}",
        },
        json={
            "name": "Produto de Teste",
            "description": "Descrição do produto de teste",
            "price": 100,
            "external_id": "1234567890",
        },
    )
    response = request.json()
    assert request.status_code == 404

@pytest.mark.anyio
@pytest.mark.order(7)
async def test_should_create_product_with_seller_authorization(client: AsyncClient):

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

    # create product
    request = await client.post(
        "/stores/1/products",
        headers={
            "Seller-Authorization": f"Bearer {response_seller_authenticated['access_token']}",
        },
        json={
            "name": "Produto de Teste",
            "description": "Descrição do produto de teste",
            "price": 100,
            "external_id": "1234567890",
        },
    )
    response = request.json()
    assert request.status_code == 200
    assert response["id"] == 1
    assert response["name"] == "Produto de Teste"
    assert response["description"] == "Descrição do produto de teste"
    assert response["price"] == 100