from pydantic import BaseModel, Field

class ProductSchema(BaseModel):
    name: str = Field()
    description: str = Field()
    price: int = Field()
    external_id: str = Field()
