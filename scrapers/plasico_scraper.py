import re
from urllib.parse import quote, urljoin
from .base_scraper import AsyncPlaywrightBaseScraper

class PlasicoScraper(AsyncPlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://plasico.bg/"
        self.current_page = 1
        self.update_gui_callback = update_gui_callback
        self.website_that_is_scraped = "Plasico.bg"
        
    def _extract_and_convert_price(self, price_text):
        if price_text == "N/A":
            return None
        
        try:
            print(f"DEBUG: Raw price text: '{price_text}'")
        
            price_text = price_text.strip()
        
            lev_match = re.search(r'([\d\s,.]+)\s*лв\.?', price_text)
            if lev_match:
                price_str = lev_match.group(1)
                price_str = price_str.replace(' ', '').replace(',', '.')
                print(f"DEBUG: Extracted lev price string: '{price_str}'")
                return float(price_str)
        
            euro_match = re.search(r'([\d\s,.]+)\s*€', price_text)
            if euro_match:
                price_str = euro_match.group(1)
                price_str = price_str.replace(' ', '').replace(',', '.')
                print(f"DEBUG: Extracted euro price string: '{price_str}'")
                return float(price_str)
        
            match = re.search(r'([\d\s,.]+)', price_text)
            if match:
                price_str = match.group(1)
                price_str = price_str.replace(' ', '').replace(',', '.')
                print(f"DEBUG: Extracted price string: '{price_str}'")
                return float(price_str)
                
        except Exception as e:
            print(f"DEBUG: Price extraction error: {e} for text: {price_text}")
    
        return None

    def _get_base_url(self, search_term):
        encoded_term = quote(search_term)
        return f"{self.base_url}tyrsene/{encoded_term}"

    def _construct_page_url(self, base_url, search_term):
        if self.current_page > 1:
            return f"{self.base_url}tyrsene/{quote(search_term)}/p{self.current_page}"
        return base_url

    async def _extract_product_links(self, page, page_url):
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            await page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
            
            await page.wait_for_selector('div#list-results', timeout=10000)

            product_elements = await page.query_selector_all('article.product-box')
            print(f"DEBUG: Found {len(product_elements)} product elements")
            
            for product in product_elements:
                if self._stop_event.is_set():
                    break

                sponsored = await product.query_selector('span:has-text("Sponsored")')
                if sponsored:
                    continue

                title_element = await product.query_selector('span.ttl')
                title = await title_element.inner_text() if title_element else ""
                if title_element:
                    title = title.strip()
                
                temp_product_data = {'title': title, 'description': ''}
                if self._should_filter_by_keywords(temp_product_data):
                    print(f'Skipped product because it was in the exclusion keywords: {self.exclude_keywords}')
                    continue

                link_element = await product.query_selector('a.mainlink[href]')
                if link_element:
                    href = await link_element.get_attribute('href')
                    if href:
                        full_url = urljoin(self.base_url, href)
                        clean_url = full_url.split('ref=')[0].split('?')[0]
                        if clean_url not in product_links:
                            product_links.append(clean_url)
                            print(f"DEBUG: Added Plasico product: {title}")

            print(f"DEBUG: Total Plasico product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from Plasico: {e}")
            return []

    async def _extract_product_data(self, page, product_url):
        print(f"DEBUG: Parsing Plasico product: {product_url}")

        try:
            await page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
    
            await page.wait_for_selector('div.details-heading h1', timeout=10000)

            title_element = await page.query_selector('div.details-heading h1')
            title = await title_element.inner_text() if title_element else "N/A"
            if title_element:
                title = title.strip()
    
            price_element = None
            price_selectors = [
                'span.price',
                '.price',
                '.details-price span.price',
                'div.details-price span.price'
            ]
        
            for selector in price_selectors:
                price_element = await page.query_selector(selector)
                if price_element:
                    class_attr = await price_element.get_attribute('class') or ''
                    if 'oldprice' not in class_attr:
                        break
                    price_element = None
        
            if price_element:
                price_text = await price_element.inner_text()
                price_text = price_text.strip()
                print(f"DEBUG: Price text extracted: '{price_text}'")
            else:
                price_text = "N/A"
                print("DEBUG: No price element found")
            
            price = self._extract_and_convert_price(price_text)
    
            product_data = {
                'title': title,
                'price': price,
                'url': product_url,
                'currency': self.website_currency,
                'source': 'Plasico.bg',
                'source_currency': self.website_currency,
                'page': self.current_page
            }

            print(f"DEBUG: Extracted Plasico product: {title} - {price}")

            tech_table = await page.query_selector('table#spec-table')
            if tech_table:
                list_items = await tech_table.query_selector_all('tr')
                for item in list_items:
                    try:
                        td_elements = await item.query_selector_all('td')
                        if len(td_elements) >= 2:
                            label_element = td_elements[0]
                            value_element = td_elements[1]
                    
                            label_text = await label_element.inner_text() if label_element else ""
                            value_text = await value_element.inner_text() if value_element else ""
                            if label_element:
                                label_text = label_text.strip().lower()
                            if value_element:
                                value_text = value_text.strip().lower()
                    
                            if value_text:
                                product_data[label_text] = value_text
                                print(f"DEBUG: Added Plasico spec: {label_text} = {value_text}")
                        else:
                            print(f"DEBUG: Skipping table row with insufficient cells: {len(td_elements)}")
                    
                    except Exception as e:
                        print(f"DEBUG: Skipping invalid property: {str(e)}")
                        continue

            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing Plasico product page: {e}")
            return None