import uuid
from fastapi import APIRouter, Request, HTTPException
from src.models import Order, OrderItem, Cart, CartItem, Product
from src.authentication import customer_required, store_required
from src.utils import get_order_details, get_cart_items

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    responses={404: {"description": "Not found"}},
)



@router.post("/")
@customer_required
@store_required
async def store(request: Request):
    cart = await get_cart_items(request.current_store.id, request.current_user.id)
    if cart["cart_empty"]:
        raise HTTPException(status_code=404, detail="Cart empty")
    
    for item in cart["items"]:
        if not await Product.filter(store_id=request.current_store.id, id=item["product_id"], status='active').first():
            raise HTTPException(status_code=404, detail=f"Product {item['product_name']} not found")

    order = await Order.create(
        status='created', 
        store_id=request.current_store.id,
        customer_id=request.current_user.id, 
        code=str(uuid.uuid4().hex)[:250]
    )

    for item in cart["items"]:
        await OrderItem.create(order_id=order.id, product_id=item["product_id"], amount=item["amount"], price=item["price"])

    return await get_order_details(order.id)
