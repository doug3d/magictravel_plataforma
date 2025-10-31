import pytest
from httpx import AsyncClient


@pytest.mark.anyio
@pytest.mark.order(11)
async def test_shouldnt_create_cart_without_customer_authorization(client: AsyncClient):
    request = await client.post(
        "/carts/",
        json={
            "product_id": 1,
            "amount": 1,
        },
    )
    assert request.status_code == 403
    assert request.json()["detail"] == "Unauthorized"

@pytest.mark.anyio
@pytest.mark.order(12)
async def test_shouldnt_create_cart_without_store(client: AsyncClient, get_authenticated_customer_access_token: str):
    # create cart
    request = await client.post(
        "/carts/",
        headers={
            "Customer-Authorization": f"Bearer {get_authenticated_customer_access_token}",
        },
        json={
            "product_id": 1,
            "amount": 1,
        },
    )
    assert request.status_code == 403
    response = request.json()
    assert response["detail"] == "Store credential is invalid"

@pytest.mark.anyio
@pytest.mark.order(13)
async def test_should_create_cart_with_customer_authorization(client: AsyncClient, 
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
    response = request.json()
    assert response["cart_empty"] == False
    assert response["items"][0]["product_id"] == 1
    assert response["items"][0]["amount"] == 1

@pytest.mark.anyio
@pytest.mark.order(14)
async def test_should_update_cart_item_amount_with_customer_authorization(client: AsyncClient, 
                            get_authenticated_customer_access_token: str, 
                            get_authenticated_store_credential: str):
    # update cart item amount
    request = await client.put(
        "/carts/update-amount",
        headers={
            "Customer-Authorization": f"Bearer {get_authenticated_customer_access_token}",
            "Store-Credential": get_authenticated_store_credential,
        },
        json={
            "product_id": 1,
            "amount": 2,
        },
    )
    assert request.status_code == 200
    response = request.json()
    assert response["cart_empty"] == False
    assert response["items"][0]["product_id"] == 1
    assert response["items"][0]["amount"] == 2

@pytest.mark.anyio
@pytest.mark.order(15)
async def test_should_delete_cart_item_with_customer_authorization(client: AsyncClient, 
                            get_authenticated_customer_access_token: str, 
                            get_authenticated_store_credential: str):
    # delete cart item
    request = await client.delete(
        "/carts/1",
        headers={
            "Customer-Authorization": f"Bearer {get_authenticated_customer_access_token}",
            "Store-Credential": get_authenticated_store_credential,
        },
    )
    assert request.status_code == 200
    response = request.json()
    assert response["cart_empty"] == True