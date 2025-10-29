from fastapi import APIRouter, HTTPException
from tortoise.exceptions import IntegrityError
from src.models import Customer, CustomerAuth
from src.dtos.customer import CustomerSchema, CustomerAuthSchema
from src.utils import generate_credentials, authenticate_user

router = APIRouter(
    prefix="/customers",
    tags=["customers"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def show():
    return await Customer.all()

@router.post("/")
async def store(body: CustomerSchema):
    try:
        customer = await Customer.create(
            name=body.name,
            email=body.email,
            password=body.password,
        )
        response = await generate_credentials(customer, 'customer')
        return response
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Email already registered")

@router.post("/auth")
async def authenticate(body: CustomerAuthSchema):
    response = await authenticate_user(body, 'customer')
    return response

