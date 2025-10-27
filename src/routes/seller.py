from fastapi import APIRouter
from src.models import Seller
from src.dtos.seller import SellerSchema
from src.utils import generate_credentials

router = APIRouter(
    prefix="/sellers",
    tags=["sellers"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def show():
    return await Seller.all()

@router.post("/")
async def store(body: SellerSchema):
    seller = await Seller.create(**body.model_dump())
    response = await generate_credentials(seller, 'seller')
    return response

