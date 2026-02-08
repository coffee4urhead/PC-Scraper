import re
from urllib.parse import quote, urljoin
from .base_scraper import AsyncPlaywrightBaseScraper

class OptimalComputersScraper(AsyncPlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://optimal-computers.bg/"
        self.website_that_is_scraped = "Optimal-Computers.bg"
        self.current_page = 1
        self.update_gui_callback = update_gui_callback

    def _get_base_url(self, search_term):
        encoded_term = quote(search_term)
        return f"{self.base_url}products/search?s={encoded_term}"

    def _construct_page_url(self, base_url, search_term):
        if self.current_page == 1:
            return base_url
        else:
            print(f"DEBUG: Optimal Computers - no pagination, stopping at page 1")
            return None
    
    async def _extract_product_links(self, page, page_url):
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            await page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
            
            await page.wait_for_selector('div.page--search-result', timeout=10000)

            product_elements = await page.query_selector_all('div.cards--products div.card-content')
            print(f"DEBUG: Found {len(product_elements)} product elements")
            
            for product in product_elements:
                if self._stop_event.is_set():
                    break

                sponsored = await product.query_selector('span:has-text("Sponsored")')
                if sponsored:
                    continue

                title_element = await product.query_selector('a.link--inherit')
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
                            print(f"DEBUG: Added Optimal Computers product: {title}")

            print(f"DEBUG: Total Optimal Computers product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from Optimal Computers: {e}")
            return []

    async def _extract_optimal_computers_price(self, price_text):
        try:
            print(f"DEBUG: Processing price text: '{price_text}'")
        
            if '/' in price_text:
                parts = price_text.split('/')
                for part in parts:
                    if 'лв' in part:
                        price_text = part.strip()
                        print(f"DEBUG: Selected BGN part: '{price_text}'")
                        break
        
            price_text = price_text.replace(' ', '')
        
            numbers = re.findall(r'[\d,.]+', price_text)
            if not numbers:
                return 0.0
            
            number = numbers[0]
            print(f"DEBUG: Extracted number: '{number}'")
        
            if ',' in number and '.' in number:
                number = number.replace(',', '')
            elif '.' in number and number.count('.') > 1:
                parts = number.split('.')

                if len(parts[-1]) <= 2:  
                    whole = ''.join(parts[:-1])
                    decimal = parts[-1]
                    number = f"{whole}.{decimal}"
                else:
                    number = number.replace('.', '')
            elif ',' in number:
                number = number.replace(' ', '').replace('.', '')
                if ',' in number:
                    parts = number.split(',')
                    if len(parts) == 2:
                        whole = parts[0]
                        decimal = parts[1]
                        number = f"{whole}.{decimal}"
        
            print(f"DEBUG: After separator cleanup: '{number}'")
        
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
        print(f"DEBUG: Parsing Optimal Computers product: {product_url}")
    
        try:
            await page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
        
            await page.wait_for_selector('div.page-header h1', timeout=10000)

            title_element = await page.query_selector('div.page-header h1')
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
                price = await self._extract_optimal_computers_price(price_text)
        
            product_data = {
                'title': title,
                'price': price,
                'url': product_url,
                'currency': self.website_currency,
                'source': 'Optimal-Computers.bg',
                'source_currency': self.website_currency,
                'page': self.current_page 
            }

            print(f"DEBUG: Extracted Optimal Computers product: {title} - {price}")

            tech_table = await page.query_selector('ul.product-characteristics')
            if tech_table:
                list_items = await tech_table.query_selector_all('li')
                for item in list_items:
                    try:
                        label_element = await item.query_selector('div.element--color-light')
                        if label_element:
                            label_text = await label_element.inner_text()
                            label_text = label_text.strip()
                            
                            full_text = await item.inner_text()
                            full_text = full_text.strip()
                            
                            value_text = full_text.replace(label_text, '').strip()
                            value_text = value_text.lstrip(':').strip()
                            
                            if label_text and value_text:
                                product_data[label_text] = value_text
                                print(f"DEBUG: Added Optimal Computers spec: {label_text} = {value_text}")
                        else:
                            print(f"DEBUG: No label found in list item")
                        
                    except Exception as e:
                        print(f"DEBUG: Skipping invalid property: {str(e)}")
                        continue

            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing Optimal Computers product page: {e}")
            return None