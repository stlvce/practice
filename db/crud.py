from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime
from decimal import Decimal
from re import sub

from parsers.perekrestok import product_perekrestok
from parsers.holodilnik import product_holodilnik

def get_price(db: Session, price_id: int):
    return db.query(models.Price).filter(models.Price.id == price_id).first()

def get_price_by_name_all(db: Session, name: str):
    return db.query(models.Price).filter(
        models.Price.name == name
    ).order_by(models.Price.datetime.desc()).all()

def get_prices(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Price).offset(skip).limit(limit).all()

# Создание товара
def create_price(db: Session, price: schemas.PriceCreate):
    dt = datetime.now()
    price_int = Decimal(sub(r"[^\d\-.]", "", price.price))
    db_price = models.Price(
        name=price.name,
        url=price.url,
        price=price.price,
        price_int=price_int,
        datetime=dt,
        store = price.store
    )
    db.add(db_price)
    db.commit()
    db.refresh(db_price)
    return db_price

# Удаление цены товара
def delete_price(db: Session, price_id: int):
    item = db.query(models.Price).filter(models.Price.id == price_id).delete()
    db.commit()
    return

# Обновление товара
def update_price(db: Session, price_id: int, price: schemas.PriceCreate):
    item = db.query(models.Price).filter(models.Price.id == price_id).first()
    item.name = price.name
    item.url = price.url
    item.price = price.price
    price_int = Decimal(sub(r"[^\d\-.]", "", price.price))
    item.price_int = price_int
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def create_price_pars(db: Session, product_url: str):
    # Перекресток
    if product_url[12:23] == "perekrestok":
        res = product_perekrestok(product_url)
    # holodilnik
    elif product_url[12:22] == "holodilnik":
        res = product_holodilnik(product_url)
    else:
        return 1

    db_price = get_price_by_name_all(db, name=res[0])
    for i in db_price:
        if i and i.price_int == res[2]:
            return 1
    else:
        dt = datetime.now()
        db_price = models.Price(
            name=res[0],
            url=product_url,
            price=res[1],
            price_int=res[2],
            datetime=dt,
            store=res[3]
        )
        db.add(db_price)
        db.commit()
        db.refresh(db_price)
        return db_price

# Запрос товаров по магазину
def get_price_by_store(db: Session, store: str):
    return db.query(models.Price).filter(
        models.Price.store == store).order_by(models.Price.datetime.desc()).all()
    