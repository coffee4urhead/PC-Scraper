import re
from urllib.parse import quote, urljoin
from .base_scraper import AsyncPlaywrightBaseScraper

class HitsBGScraper(AsyncPlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://hits.bg/"
        self.current_page = 1
        self.website_that_is_scraped = "Hits.bg"
        self.update_gui_callback = update_gui_callback

    def _get_base_url(self, search_term):
        encoded_term = quote(search_term)
        return f"{self.base_url}bg/search?search_text={encoded_term}"

    def _construct_page_url(self, base_url, search_term):
        if self.current_page > 1:
            return f"{self.base_url}bg/search?search_text={quote(search_term)}&page={self.current_page}"
        return base_url

    async def _extract_product_links(self, page, page_url):
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            await page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
            
            await page.wait_for_selector('div.catalog-grid div.grid-item', timeout=10000)

            product_elements = await page.query_selector_all('div.catalog-grid div.grid-item')
            print(f"DEBUG: Found {len(product_elements)} product elements")
            
            for product in product_elements:
                if self._stop_event.is_set():
                    break

                sponsored = await product.query_selector('span:has-text("Sponsored")')
                if sponsored:
                    continue

                title_element = await product.query_selector('a.product-name[href]')
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
                            print(f"DEBUG: Added HitsBG product: {title}")

            print(f"DEBUG: Total HitsBG product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from HitsBG: {e}")
            return []

    async def _extract_product_data(self, page, product_url):
        print(f"DEBUG: Parsing HitsBG product: {product_url}")
    
        try:
            await page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
        
            await page.wait_for_selector('span.product-status-text', timeout=10000)
            
            product_status = await page.query_selector('div.product-status')
            if product_status:
                status_text = await product_status.inner_text()
                if status_text.strip().lower() == "изчерпан":
                    print(f"DEBUG: Product is out of stock: {product_url}")
                    return None

            title_element = await page.query_selector('h1.product-title')
            title = ""
            if title_element:
                title_text = await title_element.inner_text()
                title = title_text.strip()
            else:
                title = "N/A"
        
            price_element_int = await page.query_selector_all('div.price-component.bgn div.int')
            price_element_float = await page.query_selector_all('div.price-component.bgn div.float')

            price = 0.0
            if len(price_element_int) >= 2 and len(price_element_float) >= 2:
                int_text = await price_element_int[1].inner_text()
                float_text = await price_element_float[1].inner_text()
                int_part = int_text.strip().replace('·', '').replace(' ', '')
                float_part = float_text.strip()
                price_text = f"{int_part}.{float_part}"
                print(f"DEBUG: Combined price text: '{price_text}'")
                try:
                    price = float(price_text)
                except ValueError:
                    print(f"DEBUG: Could not convert price: '{price_text}'")
            else:
                print("DEBUG: Not enough price elements found")

            product_data = {
                'title': title,
                'price': price,
                'url': product_url,
                'currency': self.website_currency,
                'source': 'Hits.bg',
                'source_currency': self.website_currency,
                'page': self.current_page
            }

            print(f"DEBUG: Extracted HitsBG product: {title} - {price}")

            tech_table = await page.query_selector('table.parameters-table')
            if tech_table:
                list_items = await tech_table.query_selector_all('tr')
                for item in list_items:
                    try:
                        td_elements = await item.query_selector_all('td')
                        if len(td_elements) >= 2:
                            label_element = td_elements[0]
                            value_element = td_elements[1]
                        
                            label_text = await label_element.inner_text()
                            value_text = await value_element.inner_text()
                            label = label_text.strip().lower()
                            value = value_text.strip().lower()
                        
                            if value:
                                product_data[label] = value
                                print(f"DEBUG: Added HitsBG spec: {label} = {value}")
                        else:
                            print(f"DEBUG: Skipping table row with insufficient cells: {len(td_elements)}")
                        
                    except Exception as e:
                        print(f"DEBUG: Skipping invalid property: {str(e)}")
                        continue

            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing HitsBG product page: {e}")
            return None