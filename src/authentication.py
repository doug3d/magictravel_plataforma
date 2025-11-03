from functools import wraps
from src.models import CustomerAuth, SellerAuth, Store
from fastapi import HTTPException, Header, Request
import datetime


async def valid_access_token(access_token: str, model: CustomerAuth | SellerAuth):
    if not access_token:
        raise HTTPException(status_code=403, detail="Unauthorized")
    access_token = access_token.split(' ')[1]
    user_auth = await model.filter(status='valid', access_token=access_token).first()
    if not user_auth:
        raise HTTPException(status_code=403, detail="Unauthorized")
    if model == CustomerAuth:
        return await user_auth.customer
    else:
        return await user_auth.seller


def get_request(kwargs):
    request = kwargs.get("request")
    if not request:
        raise RuntimeError("Request object not found in kwargs")
    return request

def customer_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = get_request(kwargs)
        access_token = request.headers.get("Customer-Authorization", False)
        user = await valid_access_token(access_token, CustomerAuth)
        request.current_user = user

        return await func(*args, **kwargs)

    return wrapper

def seller_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = get_request(kwargs)
        access_token = request.headers.get("Seller-Authorization", False)
        user = await valid_access_token(access_token, SellerAuth)
        request.current_user = user

        return await func(*args, **kwargs)

    return wrapper

def store_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = get_request(kwargs)
        credential = request.headers.get("Store-Credential", False)
        if not credential:
            raise HTTPException(status_code=403, detail="Store credential is invalid")
        store = await Store.get(credential=credential)
        if not store:
            raise HTTPException(status_code=403, detail="Store credential is invalid")
        request.current_store = store

        return await func(*args, **kwargs)

    return wrapper