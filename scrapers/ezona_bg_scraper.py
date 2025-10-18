import re
from urllib.parse import quote, urljoin
from .base_scraper import PlaywrightBaseScraper

class EZonaScraper(PlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://ezona.net/"
        self.exclude_keywords = [
            "Лаптоп", 'Настолен компютър', 'HP Victus', 'Acer Predator Helios'
        ]

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)
        return f"{self.base_url}products/search?s={encoded_term}"

    def _construct_page_url(self, base_url, search_term, page):
        if page > 1:
            return None  # EZona does not use pagination in the URL
        return base_url

    def _extract_product_links(self, page, page_url):
        """Get all product links using Playwright"""
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
            
            page.wait_for_selector('div.cards div.product', timeout=10000)

            product_elements = page.query_selector_all('div.cards div.product')
            print(f"DEBUG: Found {len(product_elements)} product elements")
            
            for product in product_elements:
                if self.stop_event.is_set():
                    break

                sponsored = product.query_selector('span:has-text("Sponsored")')
                if sponsored:
                    continue

                title_element = product.query_selector('a.link--inherit[href]')
                title = title_element.inner_text().strip() if title_element else ""
                
                if any(word.lower() in title.lower() for word in self.exclude_keywords):
                    continue

                # unavailable = product.query_selector('span.avail-old')
                # if unavailable:
                #     continue

                if title_element:
                    href = title_element.get_attribute('href')
                    if href:
                        full_url = urljoin(self.base_url, href)
                        clean_url = full_url.split('ref=')[0].split('?')[0]
                        if clean_url not in product_links:
                            product_links.append(clean_url)
                            print(f"DEBUG: Added EZona product: {title}")

            print(f"DEBUG: Total EZona product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from EZona: {e}")
            return []

    def _parse_product_page(self, page, product_url):
        """Extract detailed information using Playwright"""
        print(f"DEBUG: Parsing EZona product: {product_url}")
    
        try:
            page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
        
            page.wait_for_selector('div.product-brand h1', timeout=10000)

            title_element = page.query_selector('div.product-brand h1')
            title = title_element.inner_text().strip() if title_element else "N/A"
        
            price_element = page.query_selector('span.product-price')
            price_text = price_element.inner_text().strip() if price_element else "N/A"
            price = self._extract_and_convert_price(price_text)
        
            product_data = {
                'title': title,
                'price': price,
                'url': product_url
            }

            print(f"DEBUG: Extracted EZona product: {title} - {price}")

            tech_table = page.query_selector('ul.product-characteristics')
            if tech_table:
                list_items = tech_table.query_selector_all('li')
                for item in list_items:
                    try:
                        label_el = item.inner_text().strip()
                        value = item.query_selector('div.element--color-light').inner_text().strip()

                        if label_el and value:
                            product_data[label_el] = value
                            print(f"DEBUG: Added property - {label_el}: {value}")
                    except Exception as e:
                        print(f"DEBUG: Skipping invalid property: {str(e)}")
                        continue

            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing EZona product page: {e}")
            return None