import os
import httpx
from typing import List
from .dto import Park, ParkProduct, ParkProductDetail


class MariaApi:
    def __init__(self):
        self.base_endpoint = os.getenv('MARIA_API_ENDPOINT')

    def get_parks(self, location: str = "FL") -> List[Park]:
        r = httpx.get(f"{self.base_endpoint}/parks/")
        response = r.json()
        return [Park(**item) for item in response]

    def get_park(self, park_code: str) -> Park:
        r = httpx.get(f"{self.base_endpoint}/parks/{park_code}")
        response = r.json()
        return Park(**response)

    def get_park_products(self, park_code: str, for_date: str = None, 
                number_days: int = None, num_adults: int = None, 
                num_children: int = None, is_special: bool = None) -> List[ParkProduct]:
        params = {}
        if for_date:
            params["forDate"] = for_date
        if number_days:
            params["numberDays"] = number_days
        if num_adults:
            params["numAdults"] = num_adults
        if num_children:
            params["numChildren"] = num_children
        if is_special:
            params["isSpecial"] = is_special
        r = httpx.get(f"{self.base_endpoint}/parks/{park_code}/products", params=params)
        response = r.json()
        return [ParkProduct(**item) for item in response]

    def get_park_product_detail(self, park_code: str, product_code: str) -> ParkProductDetail:
        r = httpx.get(f"{self.base_endpoint}/parks/{park_code}/products/{product_code}")
        response = r.json()
        return ParkProductDetail(**response)