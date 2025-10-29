from fastapi import APIRouter, Request
from src.models import Store
from src.dtos.store import StoreSchema
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
    store = await Store.create(
        seller_id=request.current_user.id,
        name=body.name, 
    )
    return store

