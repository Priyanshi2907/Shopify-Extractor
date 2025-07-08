# freakins_xpath_scraper.py
import requests
from lxml import html
import time
from requests.exceptions import RequestException

# Rate Limit Handling Retries and backoff seamlessly
def fetch_with_retries(url, retries=3, backoff=1):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    for attempt in range(retries):
        try:
            response = requests.get(url,headers=headers,timeout=10)
            response.raise_for_status()
            return response
        except RequestException as e:
            print(f"[Retry {attempt+1}] Error: {e}")
            time.sleep(backoff * (2 ** attempt))
    raise Exception(f"Failed to fetch {url} after {retries} retries.")

def scrape_freakins():
    url = "https://freakins.com/collections/shop-womens-jeans"
    base_url = "https://freakins.com"

    response = fetch_with_retries(url)
    if response.status_code != 200:
        raise Exception(f"Failed to load page: {response.status_code}")

    tree = html.fromstring(response.content)
    product_cards = tree.xpath("//product-item")

    products = []
    for card in product_cards:
        try:
            title = card.xpath(".//a[contains(@class, 'product-item-meta__title')]/text()")[0].strip()
            relative_url = card.xpath(".//a[contains(@class, 'product-item-meta__title')]/@href")[0]
            full_url = base_url + relative_url

            price = card.xpath(".//div[contains(@class,'price-list')]//span[contains(@class, 'price')]/text()")[1].strip()

            image_src = card.xpath(".//img[contains(@class, 'product-item__primary-image')]/@src")
            image_url = "https:" + image_src[0] if image_src else None

            products.append({
                "product_title": title,
                "product_url": full_url,
                "price": price,
                "image_url": image_url
            })

        except Exception as e:
            print(f"Error parsing product: {e}")
            continue

    return {
        "store_name": "freakins.com",
        "products": products
    }
    
