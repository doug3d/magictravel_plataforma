from pydantic import BaseModel, Field

class CustomerSchema(BaseModel):
    name: str = Field()
    email: str = Field()
    password: str = Field()

class CustomerAuthSchema(BaseModel):
    email: str = Field()
    password: str = Field()
