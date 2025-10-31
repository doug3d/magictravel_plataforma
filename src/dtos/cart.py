from pydantic import BaseModel, Field

class CartItemSchema(BaseModel):
    product_id: int = Field()
    amount: int = Field()

class CartItemUpdateSchema(BaseModel):
    product_id: int = Field()
    amount: int = Field()
