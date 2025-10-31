import pytest
from httpx import AsyncClient


@pytest.mark.anyio
@pytest.mark.order(16)
async def test_shouldnt_create_order_without_customer_authorization(client: AsyncClient):
    request = await client.post(
        "/orders/"
    )
    assert request.status_code == 403
    assert request.json()["detail"] == "Unauthorized"


@pytest.mark.anyio
@pytest.mark.order(17)
async def test_shouldnt_create_order_without_store(client: AsyncClient, get_authenticated_customer_access_token: str):
    # create order
    request = await client.post(
        "/orders/",
        headers={
            "Customer-Authorization": f"Bearer {get_authenticated_customer_access_token}",
        },
    )
    assert request.status_code == 403
    assert request.json()["detail"] == "Store credential is invalid"

@pytest.mark.anyio
@pytest.mark.order(18)
async def test_shouldnt_create_order_without_cart(client: AsyncClient, 
                get_authenticated_customer_access_token: str, 
                get_authenticated_store_credential: str):
    # create order
    request = await client.post(
        "/orders/",
        headers={
            "Customer-Authorization": f"Bearer {get_authenticated_customer_access_token}",
            "Store-Credential": get_authenticated_store_credential,
        },
    )
    assert request.status_code == 404
    assert request.json()["detail"] == "Cart empty"


@pytest.mark.anyio
@pytest.mark.order(19)
async def test_should_create_order(client: AsyncClient, 
                get_authenticated_customer_access_token: str, 
                get_authenticated_store_credential: str):
    # create cart
    request = await client.post(
        "/carts/",
        headers={
            "Customer-Authorization": f"Bearer {get_authenticated_customer_access_token}",
            "Store-Credential": get_authenticated_store_credential,
        },
        json={
            "product_id": 1,
            "amount": 1,
        },
    )
    assert request.status_code == 200
    assert request.json()["cart_empty"] == False
    assert request.json()["items"][0]["product_id"] == 1
    assert request.json()["items"][0]["amount"] == 1

    request = await client.post(
        "/orders/",
        headers={
            "Customer-Authorization": f"Bearer {get_authenticated_customer_access_token}",
            "Store-Credential": get_authenticated_store_credential,
        },
    )
    assert request.status_code == 200
    response = request.json()
    assert response["status"] == "created"
    assert response["code"] is not None
    assert response["items"][0]["product_id"] == 1
    assert response["items"][0]["amount"] == 1
    assert response["total_price"] == 100
    assert response["created_at"] is not None