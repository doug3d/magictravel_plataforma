from fastapi import APIRouter, Request, HTTPException
from src.models import Store
from src.models import Product
from src.dtos.store import StoreSchema
from src.dtos.product import ProductSchema
from src.authentication import seller_required

router = APIRouter(
    prefix="/stores",
    tags=["stores"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
@seller_required
async def show(request: Request):
    return await Store.all()

@router.post("/")
@seller_required
async def store(request: Request, body: StoreSchema):
    response = await Store.create(
        seller_id=request.current_user.id,
        name=body.name, 
    )

    return {
        'id': response.id,
        'name': response.name,
    }


@router.post("/{store_id}/products")
@seller_required
async def store_product(request: Request, store_id: int, body: ProductSchema):

    store = await Store.get(id=store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    seller_id = await store.seller

    if store.seller_id != request.current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    response = await Product.create(
        store_id=store_id,
        name=body.name,
        description=body.description,
        price=body.price,
        external_id=body.external_id,
    )

    return response