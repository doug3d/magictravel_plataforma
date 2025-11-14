from fastapi import APIRouter, Request
from src.authentication import store_required
from src.integrations.maria_api.maria import MariaApi
from src.constants import PLATFORM_COMMISSION_PERCENTAGE
from decimal import Decimal

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
    store = request.current_store
    
    # Aplicar comissões nos preços
    products_with_commission = []
    for product in products:
        product_dict = product.model_dump(by_alias=False)
        
        # Aplicar comissões no preço
        if product_dict.get('prices') and product_dict['prices'].get('usdbrl'):
            base_price = Decimal(str(product_dict['prices']['usdbrl']['amount']))
            
            # Aplicar comissão da plataforma (5%)
            price_with_platform = base_price * (1 + PLATFORM_COMMISSION_PERCENTAGE / 100)
            
            # Aplicar comissão do seller
            seller_commission = Decimal(str(store.commission_percentage))
            final_price = price_with_platform * (1 + seller_commission / 100)
            
            # Atualizar preço no produto
            product_dict['prices']['usdbrl']['amount'] = str(final_price.quantize(Decimal('0.01')))
            product_dict['original_price'] = str(base_price)
            product_dict['platform_commission'] = str(PLATFORM_COMMISSION_PERCENTAGE)
            product_dict['seller_commission'] = str(seller_commission)
        
        products_with_commission.append(product_dict)
    
    return products_with_commission

@router.get("/parks/{park_code}/products/{product_code}")
@store_required
async def get_park_product_detail(request: Request, park_code: str, product_code: str):
    maria_client = MariaApi()
    product = maria_client.get_park_product_detail(park_code, product_code)
    store = request.current_store
    
    product_dict = product.model_dump(by_alias=False)
    
    # Aplicar comissões no preço
    if product_dict.get('starting_price') and product_dict['starting_price'].get('usdbrl'):
        base_price = Decimal(str(product_dict['starting_price']['usdbrl']['amount']))
        
        # Aplicar comissão da plataforma (5%)
        price_with_platform = base_price * (1 + PLATFORM_COMMISSION_PERCENTAGE / 100)
        
        # Aplicar comissão do seller
        seller_commission = Decimal(str(store.commission_percentage))
        final_price = price_with_platform * (1 + seller_commission / 100)
        
        # Atualizar preço no produto
        product_dict['starting_price']['usdbrl']['amount'] = str(final_price.quantize(Decimal('0.01')))
        product_dict['original_price'] = str(base_price)
        product_dict['platform_commission'] = str(PLATFORM_COMMISSION_PERCENTAGE)
        product_dict['seller_commission'] = str(seller_commission)
    
    return product_dict
