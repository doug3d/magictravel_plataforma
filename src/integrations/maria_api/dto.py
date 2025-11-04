from pydantic import BaseModel
from typing import List

class ParkLocation(BaseModel):
    city: str
    state: str

class ParkImages(BaseModel):
    cover: str
    thumbnail: str

class Park(BaseModel):
    code: str
    name: str
    description: str
    images: ParkImages
    location: ParkLocation
    attraction: str
    status: str
    translations: List[str]

class ParkProductExtension(BaseModel):
    number_days: int
    number_parks: int
    product_kind: str
    about_ticket: str
    ticket_type: str
    ticket_banner: str
    observations: str
    notes: str

class ProductPrice(BaseModel):
    amount: float
    currency: str
    symbol: str

class PricePair(BaseModel):
    original: ProductPrice
    usdbrl: ProductPrice

class ParkProduct(BaseModel):
    code: str
    ticket_name: str
    park_included: str
    park_location: ParkLocation
    is_multi_days: bool
    is_park_to_park: bool
    is_dated: bool
    is_timed: bool
    available_options: List[str]
    extensions: ParkProductExtension
    starting_price: PricePair
    is_special: bool
    status: str
    translations: List[str]