from fastapi import APIRouter, Request, HTTPException, Query
from src.models import Product
from src.authentication import store_required
from src.integrations.maria_api.maria import MariaApi
from src.constants import PLATFORM_COMMISSION_PERCENTAGE
from decimal import Decimal
import re

router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={404: {"description": "Not found"}},
)


@router.get("/by-external-code")
@store_required
async def get_or_create_product_by_external_code(
    request: Request,
    product_code: str = Query(..., min_length=1, max_length=100),
    park_code: str = Query(..., min_length=1, max_length=50),
):
    """
    Busca um produto pelo código externo (Maria API).
    Se não existir, cria após validar na Maria API.
    Retorna apenas o ID interno do produto.
    
    Proteções de segurança:
    - Valida que product_code e park_code não estão vazios
    - Verifica se produto existe na Maria API antes de criar
    - Sanitiza dados da API externa
    - Vincula produto ao store da requisição (isolamento multi-tenant)
    - Valida preço
    """
    
    # Sanitização básica: remove caracteres perigosos
    product_code = re.sub(r'[^\w\-]', '', product_code.strip())
    park_code = re.sub(r'[^\w\-]', '', park_code.strip())
    
    if not product_code or not park_code:
        raise HTTPException(status_code=400, detail="Invalid product_code or park_code")
    
    # Busca produto existente no banco (vinculado ao store)
    existing_product = await Product.filter(
        product_code=product_code,
        park_code=park_code,
        store_id=request.current_store.id
    ).first()
    
    if existing_product:
        return {"product_id": existing_product.id}
    
    # Produto não existe, buscar na Maria API para validar
    try:
        maria_client = MariaApi()
        product_detail = maria_client.get_park_product_detail(park_code, product_code)
    except Exception as e:
        raise HTTPException(
            status_code=404, 
            detail=f"Product not found in Maria API or API error: {str(e)}"
        )
    
    # Validar dados do produto
    if not product_detail.ticket_name:
        raise HTTPException(status_code=400, detail="Invalid product: missing ticket_name")
    
    # Extrair e validar preço (converter de string para centavos)
    try:
        price_str = product_detail.starting_price.usdbrl.amount
        base_price = Decimal(str(price_str))
        
        if base_price <= 0:
            raise HTTPException(status_code=400, detail="Invalid product: price must be greater than 0")
        
        # Aplicar comissão da plataforma (5%)
        price_with_platform = base_price * (1 + PLATFORM_COMMISSION_PERCENTAGE / 100)
        
        # Aplicar comissão do seller
        seller_commission = Decimal(str(request.current_store.commission_percentage))
        final_price = price_with_platform * (1 + seller_commission / 100)
        
        # Converter para centavos (arredondando)
        price_cents = int(final_price * 100)
    except (ValueError, AttributeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid product: invalid price format - {str(e)}")
    
    # Sanitizar nome (truncar e escapar)
    name = product_detail.ticket_name[:255].strip()
    
    # Montar descrição a partir dos dados disponíveis
    description_parts = []
    if product_detail.park_included:
        description_parts.append(f"Parque: {product_detail.park_included}")
    if product_detail.extensions.about_ticket:
        description_parts.append(product_detail.extensions.about_ticket[:500])
    elif product_detail.extensions.ticket_type:
        description_parts.append(f"Tipo: {product_detail.extensions.ticket_type}")
    
    description = "\n".join(description_parts) if description_parts else name
    description = description[:1000].strip()  # Limitar tamanho
    
    # Criar produto no banco (vinculado ao store da requisição)
    try:
        new_product = await Product.create(
            store_id=request.current_store.id,
            product_code=product_code,
            park_code=park_code,
            name=name,
            description=description,
            price=price_cents,
            status='active'
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error creating product: {str(e)}"
        )
    
    return {"product_id": new_product.id}

