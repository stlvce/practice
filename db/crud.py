from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from re import sub
from decimal import Decimal

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

def create_price_pars(db: Session, product_url: str):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.49"
    }
    page = requests.get(url=product_url, headers=headers)
    soup = BeautifulSoup(page.content, "lxml")

    # Перекресток
    if product_url[12:23] == "perekrestok":
        product_name = soup.find("h1",class_="sc-fubCfw cqjzZF product__title").get_text()
        product_price = soup.find("div", class_="price-new").get_text()
        product_price = product_price.replace(",", ".")
        product_price_int = Decimal(sub(r"[^\d\-.]", "", product_price))
        product_store = "perekrestok"
    
    # holodilnik
    elif product_url[12:22] == "holodilnik":
        product_name = soup.find("h1", class_="catalog-detail__title").get_text()
        product_name = product_name.strip()
        product_price = soup.find("div", class_="catalog-detail__price").get_text()
        product_price = product_price.replace(" ", "")
        product_price = product_price.strip()
        product_price_int = Decimal(sub(r"[^\d\-.]", "", product_price))
        product_store = "holodilnik"
    else:
        return 1

    db_price = get_price_by_name(db, name=product_name)
    if db_price and db_price.price_int == product_price_int:
        return 1
    else:
        dt = datetime.now()
        db_price = models.Price(
            name=product_name,
            url=product_url,
            price=product_price,
            price_int=product_price_int,
            datetime=dt,
            store=product_store
        )
        db.add(db_price)
        db.commit()
        db.refresh(db_price)
        return db_price

def get_price_by_store(db: Session, store: str):
    return db.query(models.Price).filter(
        models.Price.store == store).order_by(models.Price.datetime.desc()).all()
    