import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from db.models import Price
from datetime import datetime
from decimal import Decimal
from re import sub

def product_all(db: Session):
    PRODUCT_URL = "https://www.perekrestok.ru/cat/d?"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.62"
    }

    page = requests.get(url=PRODUCT_URL, headers=headers)
    soup = BeautifulSoup(page.content, "lxml")
    last_page = 1
    pages = list(range(1, int(last_page) + 1))

    for page in pages:
        url = 'https://www.perekrestok.ru/cat/d?page=%s' % (page)
        page = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(page.content, "lxml")
        names = soup.find_all(class_="product-card__title")
        prices = soup.find_all(class_="price-new")
        image1 = soup.find_all('a', class_='sc-fFubgz fsUTLG product-card__link')

    urls = []
    for i in image1:
        urls.append(i.get('href'))

    product_names = list(map(lambda x: x.text, names))
    product_prices = list(map(lambda x: x.text.replace(",", "."), prices))
    product_price_int = list(map(lambda x: Decimal(sub(r"[^\d\-.]", "", x)), product_prices))
    product_price_int = list(map(int, product_price_int))
    product_urls = list(map(lambda x: "https://www.perekrestok.ru" + x, urls))

    for i in range(len(product_names)):
        db.add(
            Price(name=product_names[i],
                price=product_prices[i],
                datetime=datetime.now(),
                price_int=product_price_int[i],
                store="perekrestok", 
                url=product_urls[i]
                )
        )
    db.commit()