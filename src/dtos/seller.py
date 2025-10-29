from pydantic import BaseModel, Field

class SellerSchema(BaseModel):
    name: str = Field()
    email: str = Field()
    password: str = Field()

class SellerAuthSchema(BaseModel):
    email: str = Field()
    password: str = Field()