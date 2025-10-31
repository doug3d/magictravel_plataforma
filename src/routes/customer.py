from fastapi import APIRouter, HTTPException, Request
from tortoise.exceptions import IntegrityError
from src.models import Customer, CustomerAuth
from src.dtos.customer import CustomerSchema, CustomerAuthSchema
from src.utils import generate_credentials, authenticate_user
from src.authentication import store_required

router = APIRouter(
    prefix="/customers",
    tags=["customers"],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
@store_required
async def store(request: Request, body: CustomerSchema):
    if await Customer.filter(store_id=request.current_store.id, email=body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    customer = await Customer.create(
        store_id=request.current_store.id,
        name=body.name,
        email=body.email,
        password=body.password,
    )
    response = await generate_credentials(customer, 'customer')
    return response

@router.post("/auth")
@store_required
async def authenticate(request: Request, body: CustomerAuthSchema):
    response = await authenticate_user(body, 'customer', request.current_store.id)
    return response

