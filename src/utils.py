import uuid
from src.models import CustomerAuth, SellerAuth, Customer, Seller
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


async def authenticate_user(body: CustomerAuthSchema | SellerAuthSchema, model: str):
    if model == 'customer':
        customer = await Customer.filter(email=body.email, password=body.password).first()
        if not customer:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return await generate_credentials(customer, 'customer')
    elif model == 'seller':
        seller = await Seller.filter(email=body.email, password=body.password).first()
        if not seller:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return await generate_credentials(seller, 'seller')