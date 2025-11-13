from fastapi import APIRouter, HTTPException, Request
from tortoise.exceptions import IntegrityError
from src.models import Seller, Store
from src.dtos.seller import SellerSchema, SellerAuthSchema
from src.utils import generate_credentials, authenticate_user
from src.authentication import seller_required, store_required

router = APIRouter(
    prefix="/sellers",
    tags=["sellers"],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
async def store(body: SellerSchema):
    try:
        seller = await Seller.create(
            name=body.name,
            email=body.email,
            password=body.password,
        )
        response = await generate_credentials(seller, 'seller')
        return response
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Email already registered")


@router.post("/auth")
async def authenticate(body: SellerAuthSchema):
    response = await authenticate_user(body, 'seller')
    return response


@router.get("/me")
@seller_required
async def get_seller_info(request: Request):
    """Retorna informações do seller autenticado"""
    seller = request.current_user
    
    # Buscar loja do seller (pode não existir)
    store = await Store.filter(seller=seller).first()
    
    return {
        "id": seller.id,
        "name": seller.name,
        "email": seller.email,
        "username": seller.email,  # Para compatibilidade com o frontend
        "store_id": store.id if store else None,
        "store_name": store.name if store else None,
        "store_credential": store.credential if store else None
    }