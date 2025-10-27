from pydantic import BaseModel, Field

class StoreSchema(BaseModel):
    name: str = Field()
