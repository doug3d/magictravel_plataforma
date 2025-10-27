from fastapi import APIRouter
from src.models import Customer, CustomerAuth
from src.dtos.customer import CustomerSchema
from src.utils import generate_credentials

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

