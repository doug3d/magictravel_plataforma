from pydantic import BaseModel, Field, ConfigDict
from typing import List, Union, Optional, Any

class ParkLocation(BaseModel):
    city: str
    state: str

class ParkImages(BaseModel):
    cover: str
    thumbnail: str

class Translation(BaseModel):
    language_code: str
    name: str
    description: str
    note: Optional[str] = None
    observation: Optional[str] = None

class Park(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    code: str
    name: str
    description: str
    images: ParkImages
    location: ParkLocation = Field(..., alias="parklocation")
    attraction: str
    status: Union[bool, str]
    translations: List[Translation] = []

class ParkProductExtension(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    number_days: int = Field(..., alias="numberDays")
    usage_window: int = Field(..., alias="usageWindow")
    number_parks: int = Field(..., alias="numberParks")
    product_kind: str = Field(..., alias="productKind")
    about_ticket: Optional[str] = Field(None, alias="aboutTicket")
    ticket_type: Optional[str] = Field(None, alias="ticketType")
    ticket_banner: Optional[str] = Field(None, alias="ticketBanner")
    observations: Optional[str] = None

class ProductPrice(BaseModel):
    amount: str
    currency: str
    symbol: str

class PricePair(BaseModel):
    original: ProductPrice
    usdbrl: ProductPrice

class Prices(BaseModel):
    adult: PricePair
    child: PricePair
    total: PricePair
    price_type: str = Field(..., alias="type")

class ParkProduct(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    code: str
    ticket_name: str = Field(..., alias="ticketName")
    park_included: str = Field(..., alias="parkIncluded")
    park_location: ParkLocation = Field(..., alias="parkLocation")
    is_multi_days: bool = Field(..., alias="isMultiDays")
    is_park_to_park: bool = Field(..., alias="isParkToPark")
    is_dated: bool = Field(..., alias="isDated")
    is_timed: bool = Field(..., alias="isTimed")
    available_options: List[str] = Field(..., alias="availableOptions")
    extensions: ParkProductExtension
    prices: Prices
    is_special: bool = Field(..., alias="isSpecial")
    translations: List[Translation] = []
    has_active_promo: bool = Field(..., alias="hasActivePromo")

class ParkProductDetailExtension(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    days: int
    parks: int
    product_kind: str = Field(..., alias="productKind")
    about_ticket: Optional[str] = Field(None, alias="aboutTicket")
    ticket_type: Optional[str] = Field(None, alias="ticketType")
    ticket_banner: Optional[str] = Field(None, alias="ticketBanner")
    observations: Optional[str] = None
    notes: Optional[str] = None

class ParkProductDetail(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    code: str
    ticket_name: str = Field(..., alias="ticketName")
    park_included: str = Field(..., alias="parkIncluded")
    park_location: ParkLocation = Field(..., alias="parklocation")
    is_multi_days: bool = Field(..., alias="isMultiDays")
    is_park_to_park: bool = Field(..., alias="isParkToPark")
    is_dated: bool = Field(..., alias="isDated")
    is_timed: bool = Field(..., alias="isTimed")
    available_options: List[Any] = Field(..., alias="availableOptions")  # Pode ser str ou dict
    extensions: ParkProductDetailExtension
    starting_price: PricePair = Field(..., alias="startingPrice")
    is_special: bool = Field(..., alias="isSpecial")
    status: Union[bool, str]
    translations: List[Translation] = []