from pydantic import BaseModel
from typing import List, Union


class PriceBase(BaseModel):
    name: str
    url: str = None
    price: str
    price_int: int

class Price(PriceBase):
    id: int
    store: str
    class Config:
        orm_mode = True

class PriceCreate(PriceBase):
    datetime: str