from fastapi import APIRouter
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
    customer = await Customer.create(**body.model_dump())
    response = await generate_credentials(customer, 'customer')
    return response

@router.post("/auth")
async def authenticate(body: CustomerAuthSchema):
    response = await authenticate_user(body, 'customer')
    return response

