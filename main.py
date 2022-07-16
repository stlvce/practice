from xmlrpc.client import Boolean
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db import crud, models, schemas
from db.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/prices/", response_model=List[schemas.Price])
def read_prices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    prices = crud.get_prices(db, skip=skip, limit=limit)
    return prices

@app.get("/prices/{price_id}", response_model=schemas.Price)
def read_price(price_id: int, db: Session = Depends(get_db)):
    db_price = crud.get_price(db, price_id=price_id)
    if db_price is None:
        raise HTTPException(status_code=404, detail="Price not found")
    return db_price

@app.post("/prices/", response_model=schemas.Price)
def create_price(price: schemas.PriceCreate, db: Session = Depends(get_db)):
    db_price = crud.get_price_by_name(db, name=price.name)
    if db_price and db_price.price_int == price.price_int:
        raise HTTPException(status_code=400, detail="Price already exist")
    return crud.create_price(db=db, price=price)

@app.put("/prices/{price_id}", response_model=schemas.Price)
def update_price(price_id: int, price: schemas.PriceCreate, db: Session = Depends(get_db)):
    db_price = crud.get_price(db, price_id=price_id)
    if db_price is None:
        raise HTTPException(status_code=404, detail="Price not found")
    db_price = crud.update_price(db, price_id, price)
    return  db_price

@app.delete("/prices/{price_id}", response_model=dict)
def delete_price(price_id: int, db: Session = Depends(get_db)):
    db_price = crud.get_price(db, price_id=price_id)
    if db_price is None:
        raise HTTPException(status_code=404, detail="Price not found")
    crud.delete_price(db, price_id)
    return {"status": "ok"}

@app.post("/parser/", response_model=schemas.Price)
def create_price_pars(product_url: str, db: Session = Depends(get_db)):
    db_price = crud.create_price_pars(db=db, product_url=product_url)
    if db_price == 1:
        raise HTTPException(status_code=400, detail="Price already exist")
    return db_price

@app.get("/parser/{product_store}", response_model=List[schemas.Price])
def read_prices_for_store(product_store: str, db: Session = Depends(get_db)):
    db_product = crud.get_price_by_store(db=db, store=product_store)
    if db_product:
        return db_product
    raise HTTPException(status_code=404, detail="Store not found")