from fastapi import APIRouter, Request, HTTPException
from src.models import Store
from src.models import Product
from src.dtos.store import StoreSchema
from src.dtos.product import ProductSchema
from src.authentication import seller_required, store_required
import uuid

router = APIRouter(
    prefix="/stores",
    tags=["stores"],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
@seller_required
async def store(request: Request, body: StoreSchema):
    response = await Store.create(
        seller_id=request.current_user.id,
        name=body.name, 
        credential=str(uuid.uuid4().hex)[:250],
    )

    return {
        'id': response.id,
        'name': response.name,
    }


@router.post("/{store_id}/products")
@seller_required
@store_required
async def add_product(request: Request, store_id: int, body: ProductSchema):


    seller = await request.current_store.seller

    if seller.id != request.current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    response = await Product.create(
        store_id=request.current_store.id,
        name=body.name,
        description=body.description,
        price=body.price,
        external_id=body.external_id,
    )

    return response


@router.get("/{store_id}/get-credential")
@seller_required
async def get_credential(request: Request):
    store = await Store.get(seller_id=request.current_user.id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return {
        'credential': store.credential,
    }