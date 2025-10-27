from pydantic import BaseModel, Field

class CustomerSchema(BaseModel):
    name: str = Field()
    email: str = Field()
