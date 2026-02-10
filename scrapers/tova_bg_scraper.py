import re
from urllib.parse import quote, urljoin
from .base_scraper import AsyncPlaywrightBaseScraper

class TovaBGScraper(AsyncPlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://tova.bg/"
        self.current_page = 1
        self.update_gui_callback = update_gui_callback
        self.website_that_is_scraped = "Tova.bg"

    def _get_base_url(self, search_term):
        encoded_term = quote(search_term)
        return f"{self.base_url}search.html?phrase={encoded_term}"

    def _construct_page_url(self, base_url, search_term):
        if self.current_page > 1:
            return None
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
            
            euro_match = re.search(r'(\d+[.,]?\d*)\s*€', price_text)
            if euro_match:
                price_str = euro_match.group(1)
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

    def _extract_tova_bg_price(self, price_text):
        try:
            price_text = price_text.strip()
            
            lev_match = re.search(r'(\d+[.,]?\d*)\s*лв', price_text)
            if lev_match:
                price_str = lev_match.group(1)
                price_str = price_str.replace(',', '.')
                return float(price_str)
            
            euro_match = re.search(r'(\d+[.,]?\d*)\s*€', price_text)
            if euro_match:
                price_str = euro_match.group(1)
                price_str = price_str.replace(',', '.')
                return float(price_str)
            
            numbers = re.findall(r'\d+[.,]?\d*', price_text)
            if numbers:
                price_str = numbers[0]
                price_str = price_str.replace(',', '.')
                return float(price_str)
                
        except Exception as e:
            print(f"DEBUG: TovaBG price extraction error: {e} for text: {price_text}")
        
        return None

    async def _extract_product_links(self, page, page_url):
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            await page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
            
            await page.wait_for_selector('ul.c-search-grid-page__product-grid li.twig', timeout=10000)

            product_elements = await page.query_selector_all('ul.c-search-grid-page__product-grid li.twig')
            print(f"DEBUG: Found {len(product_elements)} product elements")
            
            for product in product_elements:
                if self._stop_event.is_set():
                    break

                sponsored = await product.query_selector('span:has-text("Sponsored")')
                if sponsored:
                    continue

                title_element = await product.query_selector('a.c-product-grid__product-title-link')
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
                            print(f"DEBUG: Added TovaBG product: {title}")

            print(f"DEBUG: Total TovaBG product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from TovaBG: {e}")
            return []

    async def _extract_product_data(self, page, product_url):
        print(f"DEBUG: Parsing TovaBG product: {product_url}")
    
        try:
            await page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
        
            await page.wait_for_selector('div.c-product-page__product-name-title-wrapper h1.c-product-page__product-name', timeout=10000)

            title_element = await page.query_selector('div.c-product-page__product-name-title-wrapper h1.c-product-page__product-name')
            title = await title_element.inner_text() if title_element else "N/A"
            if title_element:
                title = title.strip()
        
            price_element = await page.query_selector('span.u-price__base__value')
            price_text = await price_element.inner_text() if price_element else "N/A"
            if price_element:
                price_text = price_text.strip()
                
            price = self._extract_tova_bg_price(price_text)

            if price is None:
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

            print(f"DEBUG: Extracted TovaBG product: {title} - {price}")

            tech_table = await page.query_selector('ul.c-tab-attributes__list')
            if tech_table:
                list_items = await tech_table.query_selector_all('li')
                for item in list_items:
                    try:
                        label_element = await item.query_selector('div.c-tab-attribute__label')
                        value_element = await item.query_selector('div.c-tab-attribute__value-wrapper')
                        
                        if label_element and value_element:
                            label = await label_element.inner_text()
                            value = await value_element.inner_text()
                            label = label.strip()
                            value = value.strip()

                            if label and value:
                                product_data[label] = value
                                print(f"DEBUG: Added property - {label}: {value}")
                    except Exception as e:
                        print(f"DEBUG: Skipping invalid property: {str(e)}")
                        continue

            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing TovaBG product page: {e}")
            return None