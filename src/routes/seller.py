from fastapi import APIRouter, HTTPException, Request
from tortoise.exceptions import IntegrityError
from src.models import Seller
from src.dtos.seller import SellerSchema, SellerAuthSchema
from src.utils import generate_credentials, authenticate_user
from src.authentication import store_required

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