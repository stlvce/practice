from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Price(BaseModel):
    name: str
    price: float

PRICES_DB = [
    Price(name="test1", price=1000),
    Price(name="test2", price=2000),
    Price(name="test3", price=100),
    Price(name="test4", price=999),
    Price(name="test5", price=10),
]

@app.get("/price")
def read_prices():
    return PRICES_DB

@app.get("/price/{item_id}")
def read_price(item_id: int):
    return PRICES_DB[item_id]

@app.post("/price/create")
def create_price(item: Price):
    PRICES_DB.append(item)
    return {"status": "ok"}

@app.put("/price/{item_id}")
def update_price(item_id: int, item: Price):
    PRICES_DB[item_id] = item
    return {"status": "ok"}

@app.delete("/price/{item_id}")
def delete_price(item_id: int):
    del PRICES_DB[item_id]
    return {"status": "ok"}