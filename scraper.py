
import requests
import time
from bs4 import BeautifulSoup
import random

def begin_scraping(search_term, max_pages=20):
    current_page = 1
    all_products = []
    has_next_page = True

    base_url = (
        f"https://www.amazon.com/s?k={search_term.replace(' ', '+')}"
        "&crid=32P9R4ODIWA9D"
        "&sprefix=nvidia+rtx+30%2Caps%2C239"
        "&ref=nb_sb_noss_2"
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    while has_next_page and current_page <= max_pages:
        print(f"Scraping page {current_page}...")
        try:
            url = f"{base_url}&page={current_page}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            if "captcha" in response.text.lower():
                print("CAPTCHA detected! Stopping scraping.")
                break

            time.sleep(2 + random.random())
            soup = BeautifulSoup(response.text, "html.parser")

            next_button = soup.find('a', {'aria-label': f'Go to next page, page {current_page + 1}'})
            has_next_page = bool(next_button)

            products = soup.find_all("div", {'data-component-type': 's-search-result'})

            for product in products:
                h2_caption = product.find("h2", attrs={'aria-label': True})
                product_name = h2_caption.get('aria-label', 'N/A') if h2_caption else 'N/A'

                price = product.find("span", class_="a-price")
                if price:
                    symbol = price.find("span", class_="a-price-symbol")
                    whole = price.find("span", class_="a-price-whole")
                    fraction = price.find("span", class_="a-price-fraction")
                    full_price = (
                        f"{symbol.get_text() if symbol else ''}"
                        f"{whole.get_text() if whole else ''}"
                        f".{fraction.get_text() if fraction else ''}"
                    )
                else:
                    full_price = "N/A"

                product_info = f"Page {current_page}: {product_name} | Price: {full_price}"
                all_products.append(product_info)
                print(product_info)

        except Exception as e:
            print(f"Error on page {current_page}: {e}")
            break

        current_page += 1

    return all_products