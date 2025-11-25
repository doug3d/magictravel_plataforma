from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from src.integrations.maria_api.maria import MariaApi

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    tags=["pages"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def index(request: Request):
    return templates.TemplateResponse("pages/index.html", {"request": request})

@router.get("/parks/{park_code}")
async def park(request: Request, park_code: str):
    maria_client = MariaApi()
    park = maria_client.get_park(park_code)
    return templates.TemplateResponse("pages/park.html", {"request": request, "park": park})

@router.get("/checkout")
async def checkout(request: Request):
    return templates.TemplateResponse("pages/checkout.html", {"request": request})

@router.get("/orders/track/{code}")
async def track_order(request: Request, code: str):
    return templates.TemplateResponse("pages/order_details.html", {"request": request})