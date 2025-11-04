import pytest
import httpx
from src.integrations.maria_api.maria import MariaApi


@pytest.mark.anyio
@pytest.mark.order(20)
async def test_should_get_parks():
    maria_client = MariaApi()
    parks = maria_client.get_parks()
    assert len(parks) > 0
    assert parks[0].code is not None
    assert parks[0].name is not None
    assert parks[0].description is not None
    assert parks[0].images is not None
    assert parks[0].location is not None
    assert parks[0].attraction is not None
    assert parks[0].status is not None
    assert parks[0].translations is not None

@pytest.mark.anyio
@pytest.mark.order(21)
async def test_should_get_park():
    maria_client = MariaApi()
    park = maria_client.get_park("bdab5664-ab6c-4cbd-817e-59a8c76b4dac")
    assert park.code is not None
    assert park.name is not None
    assert park.description is not None
    assert park.images is not None
    assert park.location is not None
    assert park.attraction is not None
    assert park.status is not None
    assert park.translations is not None

@pytest.mark.anyio
@pytest.mark.order(22)
async def test_should_get_park_products():
    maria_client = MariaApi()
    products = maria_client.get_park_products("bdab5664-ab6c-4cbd-817e-59a8c76b4dac")
    assert len(products) > 0
    assert products[0].code is not None
    assert products[0].ticket_name is not None
    assert products[0].park_included is not None
    assert products[0].park_location is not None
    assert products[0].prices is not None
    assert products[0].extensions is not None
    assert products[0].is_special is not None
    assert products[0].translations is not None


@pytest.mark.anyio
@pytest.mark.order(23)
async def test_should_get_park_product_detail():
    maria_client = MariaApi()
    product = maria_client.get_park_product_detail("bdab5664-ab6c-4cbd-817e-59a8c76b4dac", "987cedca-559e-4b71-a00b-932c5208b846")
    assert product.code is not None
    assert product.ticket_name is not None
    assert product.park_included is not None
    assert product.park_location is not None
    assert product.starting_price is not None
    assert product.extensions is not None
    assert product.is_special is not None
    assert product.status is not None
    assert product.translations is not None