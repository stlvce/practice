from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from db import crud, models, schemas
from db.database import SessionLocal, engine
from typing import List
from decimal import Decimal
from re import sub
from parsers.prod_all import product_all

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Получение всех товаров
@app.get("/prices/", response_model=List[schemas.Price])
def read_prices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    prices = crud.get_prices(db, skip=skip, limit=limit)
    return prices

# Получение товара по id
@app.get("/prices/{price_id}", response_model=schemas.Price)
def read_price(price_id: int, db: Session = Depends(get_db)):
    db_price = crud.get_price(db, price_id=price_id)
    if db_price is None:
        raise HTTPException(status_code=404, detail="Price not found")
    return db_price

# Создание товара
@app.post("/prices/", response_model=schemas.Price)
def create_price(price: schemas.PriceCreate, db: Session = Depends(get_db)):
    db_price = crud.get_price_by_name_all(db, name=price.name)
    price_int = Decimal(sub(r"[^\d\-.]", "", price.price))
    for i in db_price:
        if i and int(i.price_int) == int(price_int):
            raise HTTPException(status_code=400, detail="Price already exist")
    return crud.create_price(db=db, price=price)

# Обновление информации товара
@app.put("/prices/{price_id}", response_model=schemas.Price)
def update_price(price_id: int, price: schemas.PriceCreate, db: Session = Depends(get_db)):
    db_price = crud.get_price(db, price_id=price_id)
    if db_price is None:
        raise HTTPException(status_code=404, detail="Price not found")
    db_price = crud.update_price(db, price_id, price)
    return  db_price

# Удаление товара по id
@app.delete("/prices/{price_id}", response_model=dict)
def delete_price(price_id: int, db: Session = Depends(get_db)):
    db_price = crud.get_price(db, price_id=price_id)
    if db_price is None:
        raise HTTPException(status_code=404, detail="Price not found")
    crud.delete_price(db, price_id)
    return {"status": "ok"}

# Добавление товара с другого сайта
# Передаваемые параметры:
# 1) Ссылка товар магазина "Перекрёсток"
# 2) Ссылка товар магазина "Холодильник.RU"
# 3) all - все товары с одной страницы
@app.post("/parser/", response_model=schemas.Price)
def create_price_pars(product_url: str, db: Session = Depends(get_db)):
    # Добавление товара из определенного магазина
    if product_url[12:23] == "perekrestok" or product_url[12:22] == "holodilnik":
        db_price = crud.create_price_pars(db=db, product_url=product_url)
        if db_price == 1:
            raise HTTPException(status_code=400, detail="Price already exist")
        return db_price
    # Добавить сразу несколько товаров из Перекрестка
    elif product_url == "all":
        product_all(db=db)
    else:
        raise HTTPException(status_code=400, detail="Price already exist")

# Получение товаров из доступных магазинов
@app.get("/parser/{product_store}", response_model=List[schemas.Price])
def read_prices_for_store(product_store: str, db: Session = Depends(get_db)):
    db_product = crud.get_price_by_store(db=db, store=product_store)
    if db_product:
        return db_product
    raise HTTPException(status_code=404, detail="Store not found")