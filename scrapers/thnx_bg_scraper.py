import re
from urllib.parse import quote, urljoin
from .base_scraper import PlaywrightBaseScraper

class ThxScraper(PlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://thx.bg/"

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
                            print(f"DEBUG: Added Thx.bg product: {title}")

            print(f"DEBUG: Total Thx.bg product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from Thx.bg: {e}")
            return []

    def _extract_product_data(self, page, product_url):
        """Extract detailed information using Playwright"""
        print(f"DEBUG: Parsing Thx.bg product: {product_url}")
    
        try:
            page.goto(product_url, wait_until='load', timeout=30000)
        
            page.wait_for_selector('div.d-none h1.product-title', timeout=10000)

            title_element = page.query_selector('div.d-none h1.product-title')
            title = title_element.inner_text().strip() if title_element else "N/A"
        
            price = 0.0
            page.wait_for_selector('div.price-component.bgn', state='visible', timeout=15000)
            price_elements = page.query_selector_all('div.price-component.bgn')

            if not price_elements:
                print("DEBUG: No price elements found.")
                return None

            print(f"DEBUG: Found {len(price_elements)} price elements.")

            price_element = price_elements[-1]
            price_text = price_element.inner_text().strip()

            print(f"DEBUG: Selected Thx.bg price text: {price_text}")
            price = self._extract_thx_bg_price(price_text)
        
            if price == 0.0:
                price_elements = page.query_selector_all('[class*="price"]')
                for elem in price_elements:
                    text = elem.inner_text().strip()
                    if 'лв' in text.lower() and any(c.isdigit() for c in text):
                        extracted = self._extract_and_convert_price(text)
                        if extracted > 0:
                            price = extracted
                            print(f"DEBUG: Strategy 2 - Extracted price: {price} from '{text}'")
                            break
        
            if price == 0.0:
                meta_price = page.query_selector('meta[itemprop="price"]')
                if meta_price:
                    price_content = meta_price.get_attribute('content')
                    if price_content:
                        try:
                            price = float(price_content)
                            print(f"DEBUG: Strategy 3 - Extracted price from meta: {price}")
                        except ValueError:
                            pass
        
            product_data = {
                'title': title,
                'price': price,
                'url': product_url
            }

            print(f"DEBUG: Extracted Thx.bg product: {title} - {price}")

            tech_table = page.query_selector('table.parameters-table')
            if tech_table:
                list_items = tech_table.query_selector_all('tr')
                for item in list_items:
                    try:
                        # FIXED: Use query_selector_all and proper indexing
                        td_elements = item.query_selector_all('td')
                        if len(td_elements) >= 2:
                            label_element = td_elements[0]
                            value_element = td_elements[1]
                        
                            label = label_element.inner_text().strip().lower()
                            value = value_element.inner_text().strip().lower()
                        
                            if value:
                                product_data[label] = value
                                print(f"DEBUG: Added Thx.bg spec: {label} = {value}")
                        else:
                            print(f"DEBUG: Skipping table row with insufficient cells: {len(td_elements)}")
                        
                    except Exception as e:
                        print(f"DEBUG: Skipping invalid property: {str(e)}")
                        continue

            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing Thx.bg product page: {e}")
            return None