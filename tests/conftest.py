import pytest
from asgi_lifespan import LifespanManager
from dotenv import load_dotenv
from httpx import AsyncClient, ASGITransport
from src.application import create_application

load_dotenv()


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
async def client():
    app = create_application(fake_db=True)
    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            yield c

# create a fixture to authenticate customer
@pytest.fixture(scope="session")
async def get_authenticated_customer_access_token(client: AsyncClient, get_authenticated_store_credential: str):
    request = await client.post(
        "/customers/auth",
        headers={
            "Store-Credential": get_authenticated_store_credential,
        },
        json={
            "email": "guilherme@gmail.com",
            "password": "123456",
        },
    )
    response_customer_authenticated = request.json()
    return response_customer_authenticated["access_token"]

# create a fixture to authenticate seller
@pytest.fixture(scope="session")
async def get_authenticated_seller_access_token(client: AsyncClient):
    request = await client.post(
        "/sellers/auth",
        json={
            "email": "vendedor@magic.com",
            "password": "123456",
        },
    )
    response_seller_authenticated = request.json()
    return response_seller_authenticated["access_token"]

# create a fixture to authenticate store
@pytest.fixture(scope="session")
async def get_authenticated_store_credential(client: AsyncClient, get_authenticated_seller_access_token: str):
    request = await client.get(
        "/stores/1/get-credential",
        headers={
            "Seller-Authorization": f"Bearer {get_authenticated_seller_access_token}",
        }
    )
    response_store_authenticated = request.json()
    return response_store_authenticated['credential']