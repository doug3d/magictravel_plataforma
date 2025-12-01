import uuid
from src.models import CustomerAuth, SellerAuth, Customer, Seller, Cart, CartItem, Order, OrderItem
from src.dtos.customer import CustomerAuthSchema
from src.dtos.seller import SellerAuthSchema
from fastapi import HTTPException

async def generate_credentials(user: Customer | Seller, model: str):
    access_token = uuid.uuid4()
    
    if model == 'customer':
        await CustomerAuth.filter(customer=user).update(status='invalidated')
        customer_auth = await CustomerAuth.create(customer=user, access_token=access_token)
        return {
            'access_token': access_token,
            'customer_id': customer_auth.customer.id,
            'name': customer_auth.customer.name,
        }
    elif model == 'seller':
        await SellerAuth.filter(seller=user).update(status='invalidated')
        seller_auth = await SellerAuth.create(seller=user, access_token=access_token)
        return {
            'access_token': access_token,
            'seller_id': seller_auth.seller.id,
            'name': seller_auth.seller.name,
        }
    
    raise ValueError('Invalid model')


async def authenticate_user(body: CustomerAuthSchema | SellerAuthSchema, model: str, store_id: int = None):
    if model == 'customer':
        customer = await Customer.filter(store_id=store_id, email=body.email, password=body.password).first()
        if not customer:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return await generate_credentials(customer, 'customer')
    elif model == 'seller':
        seller = await Seller.filter(email=body.email, password=body.password).first()
        if not seller:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return await generate_credentials(seller, 'seller')


async def get_cart_items(store_id: int, customer_id: int):
    cart = await Cart.filter(store_id=store_id, customer_id=customer_id, status='active').first()
    if not cart:
        return {
            'cart_empty': True,
            'items': [],
        }

    items = []

    for item in await CartItem.filter(cart=cart.id).all():
        product = await item.product
        items.append({
            'product_id': product.id,
            'product_name': product.name,
            'price': item.price,  # Use stored price
            'amount': item.amount,
            'attributes': item.attributes
        })

    return {
        'cart_empty': False,
        'items': items,
    }


async def get_order_details(order_id: int):
    order = await Order.filter(id=order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    items = []
    total_price = 0
    for item in await OrderItem.filter(order=order.id).all():
        product = await item.product
        items.append({
            'product_id': product.id,
            'product_name': product.name,
            'price': item.price,
            'amount': item.amount,
            'attributes': item.attributes
        })
        total_price += item.price * item.amount

    return {
        'status': order.status,
        'code': order.code,
        'items': items,
        'total_price': total_price,
        'created_at': order.created_at.isoformat(),
    }