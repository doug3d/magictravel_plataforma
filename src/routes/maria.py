from fastapi import APIRouter, Request
from src.authentication import store_required
from src.integrations.maria_api.maria import MariaApi

router = APIRouter(
    prefix="/maria",
    tags=["maria"],
    responses={404: {"description": "Not found"}},
)


@router.get("/parks")
@store_required
async def get_parks(request: Request):
    maria_client = MariaApi()
    parks = maria_client.get_parks()
    return [park.model_dump(by_alias=False) for park in parks]

@router.get("/parks/{park_code}")
@store_required
async def get_park(request: Request, park_code: str):
    maria_client = MariaApi()
    park = maria_client.get_park(park_code)
    return park.model_dump(by_alias=False)

@router.get("/parks/{park_code}/products")
@store_required
async def get_park_products(request: Request, park_code: str):
    maria_client = MariaApi()
    products = maria_client.get_park_products(park_code)
    return [product.model_dump(by_alias=False) for product in products]

@router.get("/parks/{park_code}/products/{product_code}")
@store_required
async def get_park_product_detail(request: Request, park_code: str, product_code: str):
    maria_client = MariaApi()
    product = maria_client.get_park_product_detail(park_code, product_code)
    return product.model_dump(by_alias=False)
