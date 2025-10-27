from pydantic import BaseModel, Field

class SellerSchema(BaseModel):
    name: str = Field()
    email: str = Field()
