from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def fetch_html(url: str, wait_selector: str | None = None, timeout_ms: int = 8000) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=timeout_ms)
        if wait_selector:
            page.wait_for_selector(wait_selector, timeout=timeout_ms)
        html = page.content()
        browser.close()
    return html

def extract_products(html: str):
    soup = BeautifulSoup(html, "lxml")
    items = []
    for card in soup.select(".product-card, .item, .col-product"):
        title_el = card.select_one(".title, .product-title")
        price_el = card.select_one(".price, .product-price")
        title = title_el.get_text(strip=True) if title_el else None
        price = price_el.get_text(strip=True) if price_el else None
        if title:
            items.append({"title": title, "price": price})
    return items
