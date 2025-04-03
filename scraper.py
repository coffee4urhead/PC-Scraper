import requests
import time
from bs4 import BeautifulSoup


def begin_scraping(search_term):
    base_url = f"https://www.amazon.com/s?k={search_term}"

    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            time.sleep(2)

            soup = BeautifulSoup(response.text, "html.parser")

            price_tags = soup.find_all("span", class_="a-price")

            if price_tags:
                for price_tag in price_tags:

                    symbol = price_tag.find("span", class_="a-price-symbol")
                    whole = price_tag.find("span", class_="a-price-whole")
                    decimal = price_tag.find("span", class_="a-price-decimal")
                    fractional = price_tag.find("span", class_="a-price-symbol")

                    if symbol and whole and decimal and fractional:
                        full_price = f"{symbol.get_text()}{whole.get_text()}{decimal.get_text()}{fractional.get_text()}"
                        print("Price:", full_price)
                    else:
                        print("Price format is missing components.")
            else:
                print("No prices found on this page.")
        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")

    except Exception as e:
        print(f"An error occurred: {e}")


