import pytest
from httpx import AsyncClient


@pytest.mark.anyio
@pytest.mark.order(8)
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
@pytest.mark.order(9)
async def test_shouldnt_create_product_without_store(client: AsyncClient, get_authenticated_seller_access_token: str):
    # create product
    request = await client.post(
        "/stores/2/products",
        headers={
            "Seller-Authorization": f"Bearer {get_authenticated_seller_access_token}",
        },
        json={
            "name": "Produto de Teste",
            "description": "Descrição do produto de teste",
            "price": 100,
            "external_id": "1234567890",
        },
    )
    response = request.json()
    assert request.status_code == 403
    assert request.json()["detail"] == "Store credential is invalid"

@pytest.mark.anyio
@pytest.mark.order(10)
async def test_should_create_product_with_seller_authorization(client: AsyncClient, 
                            get_authenticated_seller_access_token: str, 
                            get_authenticated_store_credential: str):

    # create product
    request = await client.post(
        "/stores/1/products",
        headers={
            "Seller-Authorization": f"Bearer {get_authenticated_seller_access_token}",
            "Store-Credential": get_authenticated_store_credential,
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