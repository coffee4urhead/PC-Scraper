import re
from urllib.parse import quote, urljoin
from .base_scraper import AsyncPlaywrightBaseScraper

class HitsBGScraper(AsyncPlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://hits.bg/"

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)
        return f"{self.base_url}bg/search?search_text={encoded_term}"

    def _construct_page_url(self, base_url, search_term, page):
        if page > 1:
            return f"{self.base_url}bg/search?search_text={quote(search_term)}&page={page}"
        return base_url

    def _extract_product_links(self, page, page_url):
        """Get all product links using Playwright"""
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
            
            page.wait_for_selector('div.catalog-grid div.grid-item', timeout=10000)

            product_elements = page.query_selector_all('div.catalog-grid div.grid-item')
            print(f"DEBUG: Found {len(product_elements)} product elements")
            
            for product in product_elements:
                if self.stop_event.is_set():
                    break

                sponsored = product.query_selector('span:has-text("Sponsored")')
                if sponsored:
                    continue

                title_element = product.query_selector('a.product-name[href]')
                title = title_element.inner_text().strip() if title_element else ""
                
                temp_product_data = {'title': title, 'description': ''}
                if self._should_filter_by_keywords(temp_product_data):
                    print(f'Skipped product because it was in the exclusion keywords: {self.exclude_keywords}')
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
                            print(f"DEBUG: Added HitsBG product: {title}")

            print(f"DEBUG: Total HitsBG product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from HitsBG: {e}")
            return []

    def _extract_product_data(self, page, product_url):
        """Extract detailed information using Playwright"""
        print(f"DEBUG: Parsing HitsBG product: {product_url}")
    
        try:
            page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
        
            page.wait_for_selector('span.product-status-text', timeout=10000)
            
            product_status = page.query_selector('div.product-status')
            if product_status.inner_text().strip().lower() == "изчерпан":
                print(f"DEBUG: Product is out of stock: {product_url}")
                return None

            title_element = page.query_selector('h1.product-title')
            title = title_element.inner_text().strip() if title_element else "N/A"
        
            price_element_int = page.query_selector_all('div.price-component.bgn div.int')
            price_element_float = page.query_selector_all('div.price-component.bgn div.float')

            if len(price_element_int) >= 2 and len(price_element_float) >= 2:
                int_part = price_element_int[1].inner_text().strip().replace('·', '').replace(' ', '')
                float_part = price_element_float[1].inner_text().strip()
                price_text = f"{int_part}.{float_part}"
                print(f"DEBUG: Combined price text: '{price_text}'")
            else:
                price_text = "0.00 лв"
                print("DEBUG: Not enough price elements found, using default")

            price = float(price_text)
        
            product_data = {
                'title': title,
                'price': price,
                'url': product_url
            }

            print(f"DEBUG: Extracted HitsBG product: {title} - {price}")

            tech_table = page.query_selector('table.parameters-table')
            if tech_table:
                list_items = tech_table.query_selector_all('tr')
                for item in list_items:
                    try:
                        td_elements = item.query_selector_all('td')
                        if len(td_elements) >= 2:
                            label_element = td_elements[0]
                            value_element = td_elements[1]
                        
                            label = label_element.inner_text().strip().lower()
                            value = value_element.inner_text().strip().lower()
                        
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