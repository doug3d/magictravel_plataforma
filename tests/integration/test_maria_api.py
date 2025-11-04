import pytest
import httpx
from src.integrations.maria_api.maria import MariaApi


@pytest.mark.anyio
@pytest.mark.order(20)
async def test_should_get_parks():
    maria_client = MariaApi()
    parks = maria_client.get_parks()
    assert len(parks) > 0
    print(parks)
    assert parks[0].code is not None
    assert parks[0].name is not None
    assert parks[0].description is not None
    assert parks[0].images is not None
    assert parks[0].location is not None
    assert parks[0].attraction is not None
    assert parks[0].status is not None
    assert parks[0].translations is not None