from fastapi import APIRouter
from src.models import Store
from src.dtos.store import StoreSchema

router = APIRouter(
    prefix="/stores",
    tags=["stores"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def show():
    return await Store.all()

@router.post("/")
async def store(body: StoreSchema):
    store = await Store.create(**body.model_dump())
    return store

