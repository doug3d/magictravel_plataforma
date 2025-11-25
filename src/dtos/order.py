from pydantic import BaseModel, EmailStr
from typing import Optional

class OrderCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    customer_document: str
    customer_phone: str
    address_street: str
    address_number: str
    address_city: str
    address_state: str
    address_zip: str
