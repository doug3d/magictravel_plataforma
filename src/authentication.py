from functools import wraps
from database import get_customer_auth_by_token, get_customer_by_email, check_project_ownership
from fastapi import HTTPException, Header, Request
import datetime


async def get_customer_by_token(token: str = Header("Customer-Authorization")):
    try:
        auth_token = token.split(' ')[1]
        customer_auth = await CustomerAuth.filter(status='active', token=token).first()
        return customer_auth.customer
    except Exception as e:
        print('fail(get_customer_by_token):', str(e))
        raise HTTPException(status_code=403, detail="Customer Unauthorized")


async def get_seller_by_token(token: str = Header("Seller-Authorization")):
    try:
        auth_token = token.split(' ')[1]
        seller_auth = await SellerAuth.filter(status='active', token=token).first()
        return seller_auth.seller
    except Exception as e:
        print('fail(get_seller_by_token):', str(e))
        raise HTTPException(status_code=403, detail="Seller Unauthorized")

def customer_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request")
        if not request:
             raise RuntimeError("Request object not found in kwargs")

        token = request.headers.get("Authorization", False)
        user = await get_customer_by_token(token)
        request.current_user = user

        return await func(*args, **kwargs)

    return wrapper

def seller_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request")
        if not request:
             raise RuntimeError("Request object not found in kwargs")

        token = request.headers.get("Authorization", False)
        user = await get_seller_by_token(token)
        request.current_user = user

        return await func(*args, **kwargs)

    return wrapper