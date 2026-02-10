from urllib.parse import quote, urljoin
from .base_scraper import AsyncPlaywrightBaseScraper
import re

class XtremeScraper(AsyncPlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://xtreme.bg/"
        self.current_page = 1
        self.update_gui_callback = update_gui_callback
        self.website_that_is_scraped = "Xtreme.bg"

    def _get_base_url(self, search_term):
        encoded_term = quote(search_term)
        return f"{self.base_url}shop/search.php?search_query={encoded_term}"

    def _construct_page_url(self, base_url, search_term):
        if self.current_page > 1:
            return f"{self.base_url}shop/search.php?search_query={quote(search_term)}&p={self.current_page}"
        return base_url

    def _extract_and_convert_price(self, price_text):
        if price_text == "N/A" or not price_text:
            return None
    
        try:
            price_text = price_text.strip()
        
            lev_match = re.search(r'(\d+[.,]?\d*)\s*лв', price_text)
            if lev_match:
                price_str = lev_match.group(1)
                price_str = price_str.replace(',', '.')
                return float(price_str)
        
            euro_match = re.search(r'(\d+[.,]?\d*)\s*€|€\s*(\d+[.,]?\d*)', price_text)
            if euro_match:
                price_str = euro_match.group(1) if euro_match.group(1) else euro_match.group(2)
                price_str = price_str.replace(',', '.')
                return float(price_str)
        
            numbers = re.findall(r'\d+[.,]?\d*', price_text)
            if numbers:
                price_str = numbers[0]
                price_str = price_str.replace(',', '.')
                return float(price_str)
            
        except Exception as e:
            print(f"DEBUG: Price extraction error: {e} for text: {price_text}")
    
        return None

    async def _extract_product_links(self, page, page_url):
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            await page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
            
            await page.wait_for_selector('div.search_container', timeout=10000)

            product_elements = await page.query_selector_all('div.search_container article.product')
            print(f"DEBUG: Found {len(product_elements)} product elements")
            
            for product in product_elements:
                if self._stop_event.is_set():
                    break

                sponsored = await product.query_selector('span:has-text("Sponsored")')
                if sponsored:
                    continue

                title_element = await product.query_selector('a[href]')
                title = await title_element.inner_text() if title_element else ""
                if title_element:
                    title = title.strip()

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
                            print(f"DEBUG: Added Xtreme product: {title}")

            print(f"DEBUG: Total Xtreme product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from Xtreme: {e}")
            return []

    async def _extract_product_data(self, page, product_url):
        print(f"DEBUG: Parsing Xtreme product: {product_url}")
    
        try:
            await page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
        
            await page.wait_for_selector('div.breadcrumb_title h1#main_name', timeout=10000)

            title_element = await page.query_selector('div.breadcrumb_title h1#main_name')
            title = await title_element.inner_text() if title_element else "N/A"
            if title_element:
                title = title.strip()
        
            price_element = await page.query_selector('span#main_price')
            price_text = await price_element.inner_text() if price_element else "N/A"
            if price_element:
                price_text = price_text.strip()
                
            price = None
            if price_text != "N/A":
                try:
                    price_part = price_text.split(" / ")[0]
                    price_str = price_part.replace("лв", "").replace("€", "").strip().replace(" ", ".")
                    price = float(price_str)
                except Exception as e:
                    print(f"DEBUG: Error parsing Xtreme price: {e}, trying alternative method")
                    price = self._extract_and_convert_price(price_text)
        
            product_data = {
                'title': title,
                'price': price,
                'url': product_url,
                'currency': self.website_currency,
                'source': self.website_that_is_scraped,
                'source_currency': self.website_currency,
                'page': self.current_page
            }

            print(f"DEBUG: Extracted Xtreme product: {title} - {price}")

            tech_table = await page.query_selector('table.tech_table')
            if tech_table:
                list_items = await tech_table.query_selector_all('tr')
                for item in list_items:
                    try:
                        td_elements = await item.query_selector_all('td')
                        if len(td_elements) >= 2:
                            label_element = td_elements[0]
                            value_element = td_elements[1]
                        
                            label = await label_element.inner_text() if label_element else ""
                            value = await value_element.inner_text() if value_element else ""
                            label = label.strip()
                            value = value.strip()
                        
                            if label and value:
                                product_data[label] = value
                                print(f"DEBUG: Added Xtreme spec: {label} = {value}")
                        else:
                            print(f"DEBUG: Skipping table row with insufficient cells: {len(td_elements)}")
                        
                    except Exception as e:
                        print(f"DEBUG: Skipping invalid property: {str(e)}")
                        continue

            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing Xtreme product page: {e}")
            return None