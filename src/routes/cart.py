from fastapi import APIRouter, Request, HTTPException
from src.models import Cart, CartItem, Product
from src.dtos.cart import CartItemSchema, CartItemUpdateSchema
from src.authentication import customer_required, store_required
from src.utils import get_cart_items

router = APIRouter(
    prefix="/carts",
    tags=["carts"],
    responses={404: {"description": "Not found"}},
)


@router.get("/current")
@customer_required
@store_required
async def get_current_cart(request: Request):
    """
    Retorna os itens do carrinho atual do cliente autenticado.
    """
    return await get_cart_items(request.current_store.id, request.current_user.id)


@router.post("/")
@customer_required
@store_required
async def store(request: Request, body: CartItemSchema):

    product = await Product.filter(id=body.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.status == 'inactive':
        raise HTTPException(status_code=404, detail="Product inactive")

    cart = await Cart.filter(store_id=request.current_store.id, customer_id=request.current_user.id, status='active').first()
    if not cart:
        cart = await Cart.create(
            store_id=request.current_store.id,
            customer_id=request.current_user.id,
            status='active',
        )
    
    response = await CartItem.create(
        cart_id=cart.id,
        product_id=body.product_id,
        amount=body.amount,
    )

    return await get_cart_items(request.current_store.id, request.current_user.id)

@router.put("/update-amount")
@customer_required
@store_required
async def update_amount(request: Request, body: CartItemUpdateSchema):
    cart = await Cart.filter(store_id=request.current_store.id, customer_id=request.current_user.id, status='active').first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    cart_item = await CartItem.filter(cart=cart.id, product=body.product_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    cart_item.amount = body.amount if body.amount > 0 else 1
    await cart_item.save()

    return await get_cart_items(request.current_store.id, request.current_user.id)

@router.delete("/{product_id}")
@customer_required
@store_required
async def delete_item(request: Request, product_id: int):
    cart = await Cart.filter(store_id=request.current_store.id, customer_id=request.current_user.id, status='active').first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    cart_item = await CartItem.filter(cart=cart.id, product=product_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    await cart_item.delete()

    if not await CartItem.filter(cart=cart.id).all():
        await cart.delete()
    
    return await get_cart_items(request.current_store.id, request.current_user.id)