from pydantic import BaseModel

class PriceBase(BaseModel):
    name: str
    url: str = None
    price: str
    price_int: int
    store: str = None

class Price(PriceBase):
    id: int
    class Config:
        orm_mode = True

class PriceCreate(PriceBase):
    datetime: str