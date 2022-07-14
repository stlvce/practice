from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from re import sub
from decimal import Decimal

from db import crud

def get_price(db: Session, price_id: int):
    return db.query(models.Price).filter(models.Price.id == price_id).first()


def get_price_by_name(db: Session, name: str):
    return db.query(models.Price).filter(
        models.Price.name == name
    ).order_by(models.Price.datetime.desc()).first()


def get_prices(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Price).offset(skip).limit(limit).all()

# Создание товара
def create_price(db: Session, price: schemas.PriceCreate):
    dt = datetime.now()
    db_price = models.Price(
        name=price.name,
        url=price.url,
        price=price.price,
        price_int=price.price_int,
        datetime=dt
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
    item.price_int = price.price_int
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def create_price_pars(db: Session, price: schemas.PriceCreate):
    PRODUCT_URL = price.url
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.49"
    }
    
    page = requests.get(url=PRODUCT_URL, headers=headers)
    soup = BeautifulSoup(page.content, "lxml")
    
    product_name = soup.find("h1",class_="sc-fubCfw cqjzZF product__title").get_text()
    product_price = soup.find("div", class_="price-new").get_text()
    product_price = product_price.replace(",", ".")
    product_price_int = Decimal(sub(r"[^\d\-.]", "", product_price))

    dt = datetime.now()
    db_price = models.Price(
        name=product_name,
        url=PRODUCT_URL,
        price=product_price,
        price_int=product_price_int,
        datetime=dt
    )
    db.add(db_price)
    db.commit()
    db.refresh(db_price)
    return db_price

