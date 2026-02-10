import re
from urllib.parse import quote, urljoin
from .base_scraper import AsyncPlaywrightBaseScraper

class SeneticScraper(AsyncPlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://www.senetic.bg/"
        self.current_page = 1
        self.update_gui_callback = update_gui_callback
        self.website_that_is_scraped = "Senetic.bg"
        
    def _extract_and_convert_price(self, price_text):
        if price_text == "N/A":
            return None
    
        try:
            print(f"DEBUG: Raw price text: '{price_text}'")
        
            price_text = price_text.strip()
        
            lev_match = re.search(r'([\d\s\u00A0,]+?)\s*лв', price_text)
            if lev_match:
                price_str = lev_match.group(1)
                price_str = re.sub(r'[\s\u00A0,]+', '', price_str)
                print(f"DEBUG: Raw lev price string after cleanup: '{price_str}'")
                if price_str and len(price_str) > 2:
                    price_str = price_str[:-2] + '.' + price_str[-2:]
                print(f"DEBUG: Extracted lev price string: '{price_str}'")
                return float(price_str)
        
            euro_match = re.search(r'([\d\s\u00A0,]+?)\s*€', price_text)
            if euro_match:
                price_str = euro_match.group(1)
                price_str = re.sub(r'[\s\u00A0,]+', '', price_str)
                print(f"DEBUG: Raw euro price string after cleanup: '{price_str}'")
                if price_str and len(price_str) > 2:
                    price_str = price_str[:-2] + '.' + price_str[-2:]
                print(f"DEBUG: Extracted euro price string: '{price_str}'")
                return float(price_str)
        
            all_numbers = re.findall(r'[\d\s\u00A0,]+', price_text)
            if all_numbers:
                cleaned_numbers = [re.sub(r'[\s\u00A0,]+', '', num) for num in all_numbers]
                print(f"DEBUG: All numbers found: {cleaned_numbers}")
            
                if len(cleaned_numbers) >= 2:
                    if self.website_currency.lower() == 'eur' or '€' in price_text.lower():
                        price_str = cleaned_numbers[0]
                    else:
                        price_str = cleaned_numbers[-1]
                else:
                    price_str = cleaned_numbers[0]
            
                if price_str and len(price_str) > 2:
                    price_str = price_str[:-2] + '.' + price_str[-2:]
                print(f"DEBUG: Selected price string: '{price_str}'")
                return float(price_str)
                
        except Exception as e:
            print(f"DEBUG: Price extraction error: {e} for text: {price_text}")
    
        return None

    def _get_base_url(self, search_term):
        encoded_term = quote(search_term)
        return f"{self.base_url}search/?q={encoded_term}"

    def _construct_page_url(self, base_url, search_term):
        return base_url

    async def _extract_product_links(self, page, page_url):
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            await page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
            
            await page.wait_for_selector('div.listing-products__container div.product-block', timeout=10000)

            product_elements = await page.query_selector_all('div.listing-products__container div.product-block')
            print(f"DEBUG: Found {len(product_elements)} product elements")
            
            for product in product_elements:
                if self._stop_event.is_set():
                    break

                sponsored = await product.query_selector('span:has-text("Sponsored")')
                if sponsored:
                    continue

                title_element = await product.query_selector('h3.name')
                title = await title_element.inner_text() if title_element else ""
                if title_element:
                    title = title.strip()
                
                temp_product_data = {'title': title, 'description': ''}
                if self._should_filter_by_keywords(temp_product_data):
                    print(f'Skipped product because it was in the exclusion keywords: {self.exclude_keywords}')
                    continue

                link_element = await product.query_selector('a.product-link-events[href]')
                if link_element:
                    href = await link_element.get_attribute('href')
                    if href:
                        full_url = urljoin(self.base_url, href)
                        clean_url = full_url.split('ref=')[0].split('?')[0]
                        if clean_url not in product_links:
                            product_links.append(clean_url)
                            print(f"DEBUG: Added Senetic product: {title}")

            print(f"DEBUG: Total Senetic product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from Senetic: {e}")
            return []

    async def _extract_product_data(self, page, product_url):
        print(f"DEBUG: Parsing Senetic product: {product_url}")
    
        try:
            await page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
        
            await page.wait_for_selector('div.top-info__main h1.top-info__title', timeout=10000)

            title_element = await page.query_selector('div.top-info__main h1.top-info__title')
            title = await title_element.inner_text() if title_element else "N/A"
            if title_element:
                title = title.strip()
        
            price_element = await page.query_selector('div.gross-price')
            price_text = await price_element.inner_text() if price_element else "N/A"
            if price_element:
                price_text = price_text.strip()
            price = self._extract_and_convert_price(price_text)
        
            product_data = {
                'title': title,
                'price': price,
                'url': product_url,
                'currency': self.website_currency,
                'source': 'Senetic.bg',
                'source_currency': self.website_currency,
                'page': self.current_page
            }

            print(f"DEBUG: Extracted Senetic product: {title} - {price}")

            tech_table = await page.query_selector('div.new-specification')
            if tech_table:
                list_items = await tech_table.query_selector_all('div.features-group-row')
                for item in list_items:
                    try:
                        label_element = await item.query_selector('div.single-feature-label')
                        value_element = await item.query_selector('div.single-feature-value')
                        
                        if label_element and value_element:
                            label = await label_element.inner_text()
                            value = await value_element.inner_text()
                            label = label.strip()
                            value = value.strip()
                            
                            if label and value:
                                product_data[label] = value
                                print(f"DEBUG: Added Senetic spec: {label} = {value}")
                    except Exception as e:
                        print(f"DEBUG: Skipping invalid property: {str(e)}")
                        continue

            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing Senetic product page: {e}")
            return None