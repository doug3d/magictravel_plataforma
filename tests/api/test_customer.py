import pytest
from httpx import AsyncClient


@pytest.mark.anyio
@pytest.mark.order(5)
async def test_shouldnt_create_customer_without_store(client: AsyncClient):
    request = await client.post(
        "/customers/",
        json={
            "name": "Guilherme",
            "email": "guilherme@gmail.com",
            "password": "123456",
        },
    )
    response = request.json()
    assert request.status_code == 403
    assert response["detail"] == "Store credential is invalid"

@pytest.mark.anyio
@pytest.mark.order(6)
async def test_should_create_customer(client: AsyncClient, get_authenticated_store_credential: str):
    request = await client.post(
        "/customers/",
        headers={
            "Store-Credential": get_authenticated_store_credential,
        },
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

@pytest.mark.anyio
@pytest.mark.order(7)
async def test_shouldnt_create_customer_with_same_email(client: AsyncClient, get_authenticated_store_credential: str):
    request = await client.post(
        "/customers/",
        headers={
            "Store-Credential": get_authenticated_store_credential,
        },
        json={
            "name": "Guilherme",
            "email": "guilherme@gmail.com",
            "password": "123456",
        },
    )
    assert request.status_code == 400
    response = request.json()
    assert response["detail"] == "Email already registered"