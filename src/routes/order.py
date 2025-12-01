import uuid
from fastapi import APIRouter, Request, HTTPException
from src.models import Order, OrderItem, Cart, CartItem, Product
from src.authentication import customer_required, store_required
from src.utils import get_order_details, get_cart_items
from src.dtos.order import OrderCreate
from tortoise.expressions import Q

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    responses={404: {"description": "Not found"}},
)



@router.post("/")
@customer_required
@store_required
async def store(request: Request, body: OrderCreate):
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
        code=str(uuid.uuid4().hex)[:250],
        # Customer details
        customer_name=body.customer_name,
        customer_email=body.customer_email,
        customer_document=body.customer_document,
        customer_phone=body.customer_phone,
        # Address
        address_street=body.address_street,
        address_number=body.address_number,
        address_city=body.address_city,
        address_state=body.address_state,
        address_zip=body.address_zip
    )

    for item in cart["items"]:
        await OrderItem.create(
            order_id=order.id, 
            product_id=item["product_id"], 
            amount=item["amount"], 
            price=item["price"],
            attributes=item.get("attributes", {})
        )

    return await get_order_details(order.id)


@router.get("/{code}")
async def get_order_by_code(code: str):
    """
    Public endpoint to track order by code
    """
    order = await Order.filter(code=code).prefetch_related('orderitem_order__product').first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    items = await order.orderitem_order.all().prefetch_related('product')
    
    items_data = []
    for item in items:
        items_data.append({
            "product_name": item.product.name,
            "amount": item.amount,
            "price": item.price
        })
        
    return {
        "id": order.id,
        "code": order.code,
        "status": order.status,
        "created_at": order.created_at.isoformat(),
        "customer_name": order.customer_name,
        "customer_email": order.customer_email,
        "customer_document": order.customer_document,
        "customer_phone": order.customer_phone,
        "address_street": order.address_street,
        "address_number": order.address_number,
        "address_city": order.address_city,
        "address_state": order.address_state,
        "address_zip": order.address_zip,
        "items": items_data
    }


@router.post("/{code}/pay")
async def simulate_payment(code: str):
    """
    Simulate payment for an order
    """
    order = await Order.filter(code=code).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if order.status == 'cancelled':
        raise HTTPException(status_code=400, detail="Cannot pay cancelled order")
        
    if order.status in ['paid', 'delivered']:
        return {"message": "Order already paid"}
        
    order.status = 'paid'
    await order.save()
    
    return {"message": "Payment successful", "status": order.status}
