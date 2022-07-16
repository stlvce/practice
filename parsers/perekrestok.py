import requests
from bs4 import BeautifulSoup
from re import sub
from decimal import Decimal

def product_perekrestok(product_url: str):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.49"
    }   
    page = requests.get(url=product_url, headers=headers)
    soup = BeautifulSoup(page.content, "lxml")
    
    product_name = soup.find("h1",class_="sc-fubCfw cqjzZF product__title").get_text()
    product_price = soup.find("div", class_="price-new").get_text()
    product_price = product_price.replace(",", ".")
    product_price_int = Decimal(sub(r"[^\d\-.]", "", product_price))
    product_store = "perekrestok"

    return [product_name, product_price, product_price_int, product_store]

