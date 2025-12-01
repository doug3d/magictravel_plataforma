from pydantic import BaseModel, Field

class CartItemSchema(BaseModel):
    product_id: int = Field()
    amount: int = Field()
    price: int = Field()
    attributes: dict = Field(default={})

class CartItemUpdateSchema(BaseModel):
    product_id: int = Field()
    amount: int = Field()
