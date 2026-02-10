import re
from urllib.parse import quote, urljoin
from .base_scraper import AsyncPlaywrightBaseScraper

class TehnikStoreScraper(AsyncPlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://tehnik.store/"
        self.current_page = 1
        self.update_gui_callback = update_gui_callback
        self.website_that_is_scraped = "TehnikStore.bg"

    def _get_base_url(self, search_term):
        encoded_term = quote(search_term)
        return f"{self.base_url}?s={encoded_term}&product_cat=0&post_type=product"

    def _construct_page_url(self, base_url, search_term):
        if self.current_page > 1:
            item_from = (self.current_page - 1) * 30
            return f"{self.base_url}?s={quote(search_term)}&product_cat=0&post_type=product&orderby=relevance&app={item_from}"
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

    async def _extract_product_links(self, page, page_url):
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            await page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
            
            await page.wait_for_selector('div.products', timeout=10000)

            product_elements = await page.query_selector_all('div.products div.product')
            print(f"DEBUG: Found {len(product_elements)} product elements")
            
            for product in product_elements:
                if self._stop_event.is_set():
                    break

                sponsored = await product.query_selector('span:has-text("Sponsored")')
                if sponsored:
                    continue

                title_element = await product.query_selector('h2.woocommerce-loop-product__title')
                title = await title_element.inner_text() if title_element else ""
                if title_element:
                    title = title.strip()
                
                temp_product_data = {'title': title, 'description': ''}
                if self._should_filter_by_keywords(temp_product_data):
                    print(f'Skipped product because it was in the exclusion keywords: {self.exclude_keywords}')
                    continue

                link_element = await product.query_selector('a.woocommerce-LoopProduct-link[href]')
                if link_element:
                    href = await link_element.get_attribute('href')
                    if href:
                        full_url = urljoin(self.base_url, href)
                        clean_url = full_url.split('ref=')[0].split('?')[0]
                        if clean_url not in product_links:
                            product_links.append(clean_url)
                            print(f"DEBUG: Added TehnikStore product: {title}")

            print(f"DEBUG: Total TehnikStore product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from TehnikStore: {e}")
            return []

    async def _extract_product_data(self, page, product_url):
        print(f"DEBUG: Parsing TehnikStore product: {product_url}")

        try:
            await page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
    
            await page.wait_for_selector('div.single-product-header h1.product_title', timeout=10000)

            title_element = await page.query_selector('div.single-product-header h1.product_title')
            title = await title_element.inner_text() if title_element else "N/A"
            if title_element:
                title = title.strip()

            price_element_discounted = await page.query_selector('p.price ins[aria-hidden=true] span.woocommerce-Price-amount.amount')
            price_element = await page.query_selector('p.price span.woocommerce-Price-amount.amount bdi')

            price_text = "N/A"
            if price_element_discounted:
                price_text = await price_element_discounted.inner_text() if price_element_discounted else "N/A"
            elif price_element:
                price_text = await price_element.inner_text() if price_element else "N/A"
            
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

            print(f"DEBUG: Extracted TehnikStore product: {title} - {price}")

            tech_section = await page.query_selector('div.woocommerce-Tabs-panel')
            if tech_section:
                spec_rows = await tech_section.query_selector_all('tr')
                if spec_rows:
                    for row in spec_rows:
                        try:
                            cells = await row.query_selector_all('td')
                            if len(cells) >= 2:
                                key = await cells[0].inner_text()
                                value = await cells[1].inner_text()
                                key = key.strip()
                                value = value.strip()
                                if key and value:
                                    product_data[key] = value
                                    print(f"DEBUG: Added spec (table): {key} = {value}")
                        except Exception as e:
                            print(f"DEBUG: Skipping table row: {str(e)}")
                else:
                    list_items = await tech_section.query_selector_all('li')
                    for item in list_items:
                        try:
                            text = await item.inner_text()
                            text = text.strip()
                            if ':' in text:
                                parts = text.split(':', 1)
                                if len(parts) == 2:
                                    key = parts[0].strip()
                                    value = parts[1].strip()
                                    if key and value:
                                        product_data[key] = value
                                        print(f"DEBUG: Added spec (list): {key} = {value}")
                        except Exception as e:
                            print(f"DEBUG: Skipping list item: {str(e)}")

            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing TehnikStore product page: {e}")
            return None