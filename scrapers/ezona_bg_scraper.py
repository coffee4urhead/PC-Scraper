import re
import asyncio
from urllib.parse import quote, urljoin
from .base_scraper import AsyncPlaywrightBaseScraper

class EZonaScraper(AsyncPlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://ezona.net/"
        self.website_that_is_scraped = "EZona.net"
        self.current_page = 1
        self.update_gui_callback = update_gui_callback

    def _get_base_url(self, search_term):
        encoded_term = quote(search_term)
        return f"{self.base_url}products/search?s={encoded_term}"

    def _construct_page_url(self, base_url, search_term):
        return base_url

    async def _extract_product_links(self, page, page_url):
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            await page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
            
            await page.wait_for_selector('div.cards div.product', timeout=10000)

            product_elements = await page.query_selector_all('div.cards div.product')
            print(f"DEBUG: Found {len(product_elements)} product elements")
            
            for product in product_elements:
                if self._stop_event.is_set():
                    break

                sponsored = await product.query_selector('span:has-text("Sponsored")')
                if sponsored:
                    continue

                title_element = await product.query_selector('a.link--inherit[href]')
                title = ""
                if title_element:
                    title_text = await title_element.inner_text()
                    title = title_text.strip()
                
                temp_product_data = {'title': title, 'description': ''}
                if self._should_filter_by_keywords(temp_product_data):
                    print(f'Skipped product because it was in the exclusion keywords: {self.exclude_keywords}')
                    continue

                if title_element:
                    href = await title_element.get_attribute('href')
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

    async def _extract_ezona_bg_price(self, price_text):
        try:
            print(f"DEBUG: Processing price text: '{price_text}'")
        
            if '/' in price_text:
                parts = price_text.split('/')
                for part in parts:
                    if 'лв' in part:
                        price_text = part.strip()
                        print(f"DEBUG: Selected BGN part: '{price_text}'")
                        break
        
            match = re.search(r'([\d,]+)', price_text)
            if not match:
                return 0.0
            
            number = match.group(1)
            print(f"DEBUG: Extracted number: '{number}'")
        
            number = number.replace(',', '')
        
            if len(number) > 2:
                whole_part = number[:-2]
                decimal_part = number[-2:]
                clean_price = f"{whole_part}.{decimal_part}"
            else:
                clean_price = f"0.{number:0>2}"
        
            print(f"DEBUG: Cleaned price: '{clean_price}'")
        
            if clean_price:
                result = float(clean_price)
                print(f"DEBUG: Converted '{price_text}' -> {result}")
                return result
            
            return 0.0
        
        except ValueError:
            print(f"DEBUG: Could not convert price: '{price_text}'")
            return 0.0

    async def _extract_product_data(self, page, product_url):
        print(f"DEBUG: Parsing EZona product: {product_url}")
    
        try:
            await page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
        
            await page.wait_for_selector('div.product-brand h1', timeout=10000)

            title_element = await page.query_selector('div.product-brand h1')
            title = ""
            if title_element:
                title_text = await title_element.inner_text()
                title = title_text.strip()
            else:
                title = "N/A"
        
            price_element = await page.query_selector('span.product-price')
            price = 0.0
            if price_element:
                price_text = await price_element.inner_text()
                price_text = price_text.strip()
                price = await self._extract_ezona_bg_price(price_text)
        
            product_data = {
                'title': title,
                'price': price,
                'url': product_url,
                'currency': self.website_currency,
                'source': 'EZona.net',
                'source_currency': self.website_currency,
                'page': self.current_page
            }

            print(f"DEBUG: Extracted EZona product: {title} - {price}")

            tech_table = await page.query_selector('ul.product-characteristics')
            if tech_table:
                list_items = await tech_table.query_selector_all('li')
                for item in list_items:
                    try:
                        label_text = await item.inner_text()
                        label_el = label_text.strip()
                        value_element = await item.query_selector('div.element--color-light')
                        value = ""
                        if value_element:
                            value_text = await value_element.inner_text()
                            value = value_text.strip()

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