import re
from urllib.parse import quote, urljoin
from .base_scraper import AsyncPlaywrightBaseScraper

class JarComputersScraper(AsyncPlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://www.jarcomputers.com/"
        self.website_that_is_scraped = "JarComputers.com"
        self.current_page = 1
        self.update_gui_callback = update_gui_callback

    def _get_base_url(self, search_term):
        encoded_term = quote(search_term)
        return f"{self.base_url}search?q={encoded_term}"

    def _construct_page_url(self, base_url, search_term):
        if self.current_page > 1:
            return f"{self.base_url}search?q={quote(search_term)}&ref=&page={self.current_page}"
        return base_url

    async def _extract_product_links(self, page, page_url):
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            await page.goto(page_url, wait_until='domcontentloaded', timeout=30000)

            await page.wait_for_selector('ol#product_list', timeout=10000)
            
            product_elements = await page.query_selector_all('ol#product_list li[class*="sProduct"]')
            print(f"DEBUG: Found {len(product_elements)} product elements")
            
            for product in product_elements:
                if self._stop_event.is_set():
                    break

                sponsored = await product.query_selector('span:has-text("Sponsored")')
                if sponsored:
                    continue

                title_element = await product.query_selector('span.short_title.fn')
                title = ""
                if title_element:
                    title_text = await title_element.inner_text()
                    title = title_text.strip()

                temp_product_data = {'title': title, 'description': ''}
                if self._should_filter_by_keywords(temp_product_data):
                    print(f'Skipped product because it was in the exclusion keywords: {self.exclude_keywords}')
                    continue

                unavailable = await product.query_selector('span.avail-old')
                if unavailable:
                    continue

                link_element = await product.query_selector('a[href]')
                if link_element:
                    href = await link_element.get_attribute('href')
                    if href:
                        full_url = urljoin(self.base_url, href)
                        clean_url = full_url.split('ref=')[0].split('?')[0]
                        if clean_url not in product_links:
                            product_links.append(clean_url)
                            print(f"DEBUG: Added JarComputers product: {title}")

            print(f"DEBUG: Total JarComputers product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from JarComputers: {e}")
            return []

    async def _extract_jar_computers_price(self, price_text):
        try:
            print(f"DEBUG: Processing price text: '{price_text}'")
        
            if '/' in price_text:
                parts = price_text.split('/')
                for part in parts:
                    if 'лв' in part:
                        price_text = part.strip()
                        print(f"DEBUG: Selected BGN part: '{price_text}'")
                        break
        
            numbers = re.findall(r'[\d.]+', price_text)
            if not numbers:
                return 0.0
            
            number = numbers[0]
        
            if '.' in number:
                parts = number.split('.')
                if len(parts) == 2:
                    whole_part = parts[0]
                    decimal_part = parts[1]
                    if len(decimal_part) > 2:
                        decimal_part = decimal_part[:2]
                    clean_price = f"{whole_part}.{decimal_part}"
                else:
                    clean_price = number
            else:
                if len(number) > 2:
                    whole_part = number[:-2]
                    decimal_part = number[-2:]
                    clean_price = f"{whole_part}.{decimal_part}"
                else:
                    clean_price = f"0.{number:0>2}"
        
            clean_price = re.sub(r'[^\d.]', '', clean_price)
        
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
        print(f"DEBUG: Parsing JarComputers product: {product_url}")
        
        try:
            await page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
            
            await page.wait_for_selector('div#product_name', timeout=10000)
            
            title_element = await page.query_selector('div#product_name h1')
            title = ""
            if title_element:
                title_text = await title_element.inner_text()
                title = title_text.strip()
            else:
                title = "N/A"
            
            price_element = await page.query_selector('div.price')
            price = 0.0
            if price_element:
                price_text = await price_element.inner_text()
                price_text = price_text.strip()
                price = await self._extract_jar_computers_price(price_text)
            
            product_data = {
                'title': title,
                'price': price,
                'url': product_url,
                'currency': self.website_currency,
                'source': 'JarComputers.com',
                'source_currency': self.website_currency,
                'page': self.current_page
            }

            print(f"DEBUG: Extracted JarComputers product: {title} - {price}")
            
            tech_table = await page.query_selector('ul.pprop')
            if tech_table:
                list_items = await tech_table.query_selector_all('li')
                for item in list_items:
                    try:
                        label_text = await item.inner_text()
                        label = label_text.strip().lower()
                        value_element = await item.query_selector('b')
                        value = ""
                        if value_element:
                            value_text = await value_element.inner_text()
                            value = value_text.strip()
                        if value:
                            product_data[label] = value
                            print(f"DEBUG: Added JarComputers spec: {label} = {value}")
                    except Exception as e:
                        print(f"DEBUG: Skipping invalid property: {str(e)}")
                        continue

            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing JarComputers product page: {e}")
            return None