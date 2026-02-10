import re
from urllib.parse import quote, urljoin
from .base_scraper import AsyncPlaywrightBaseScraper

class PICBgScraper(AsyncPlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://www.pic.bg/"
        self.current_page = 1
        self.update_gui_callback = update_gui_callback
        self.website_that_is_scraped = "PIC.bg"

    def _extract_and_convert_price(self, price_text):
        if price_text == "N/A":
            return None
        
        try:
            print(f"DEBUG: Raw price text: '{price_text}'")
        
            price_text = price_text.strip()
        
            lev_patterns = [
                r'([\d\s,]+)\s*€\.?',  
                r'€\.?\s*([\d\s,]+)',  
            ]
        
            for pattern in lev_patterns:
                lev_match = re.search(pattern, price_text)
                if lev_match:
                    price_str = lev_match.group(1)
                    price_str = price_str.replace(' ', '').replace(',', '')
                    if len(price_str) > 2:
                        price_str = price_str[:-2] + '.' + price_str[-2:]
                    print(f"DEBUG: Extracted lev price string: '{price_str}'")
                    return float(price_str)
        
            all_numbers = re.findall(r'[\d\s,]+', price_text)
            if all_numbers:
                cleaned_numbers = [num.replace(' ', '').replace(',', '') for num in all_numbers]
                print(f"DEBUG: All numbers found: {cleaned_numbers}")
            
                if len(cleaned_numbers) >= 2:
                    if self.website_currency.lower() == 'eur' or '€' in price_text.lower():
                        price_str = cleaned_numbers[0]
                    else:
                        price_str = cleaned_numbers[-1]
                else:
                    price_str = cleaned_numbers[0]
            
                if len(price_str) > 2:
                    price_str = price_str[:-2] + '.' + price_str[-2:]
                print(f"DEBUG: Selected price string: '{price_str}'")
                return float(price_str)
                
        except Exception as e:
            print(f"DEBUG: Price extraction error: {e} for text: {price_text}")
    
        return None

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)
        return f"{self.base_url}search/{encoded_term}"

    def _construct_page_url(self, base_url, search_term):
        if self.current_page > 1:
            return f"{self.base_url}search/{quote(search_term)}/filter/page/{self.current_page}"
        return base_url

    async def _extract_product_links(self, page, page_url):
        """Get all product links using Playwright - corrected for actual HTML structure"""
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            await page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
        
            await page.wait_for_selector('div.res-page', timeout=10000)

            results_container = await page.query_selector('div.res-page')
            if not results_container:
                print("DEBUG: No results container found")
                return []

            product_elements = await results_container.query_selector_all('div.product-item-holder-new')
            print(f"DEBUG: Found {len(product_elements)} product-item-holder-new elements")
        
            for i, product in enumerate(product_elements):
                if self._stop_event.is_set():
                    break

                print(f"DEBUG: Processing product {i+1}/{len(product_elements)}")
            
                sponsored = await product.query_selector('span:has-text("Sponsored"), div:has-text("Sponsored")')
                if sponsored:
                    print(f"DEBUG: Product {i+1} is sponsored, skipping")
                    continue

                title_element = await product.query_selector('span.ttl, .product-title, .title, a[href] span')
                title = await title_element.inner_text() if title_element else ""
                if title_element:
                    title = title.strip()
                print(f"DEBUG: Product {i+1} title: '{title}'")
            
                temp_product_data = {'title': title, 'description': ''}
                if self._should_filter_by_keywords(temp_product_data):
                    print(f'Skipped product because it was in the exclusion keywords: {self.exclude_keywords}')
                    continue

                link_element = await product.query_selector('a[href]')
                if link_element:
                    href = await link_element.get_attribute('href')
                    if href:
                        full_url = urljoin(self.base_url, href)
                        clean_url = full_url.split('ref=')[0].split('?')[0]
                        product_links.append(clean_url)
                        print(f"DEBUG: Added PIC.bg product: '{title}' -> {clean_url}")
                else:
                    print(f"DEBUG: Product {i+1} has no link element")

            print(f"DEBUG: Total PIC.bg product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from PIC.bg: {e}")
            return []

    async def _extract_product_data(self, page, product_url):
        """Extract detailed information using Playwright"""
        print(f"DEBUG: Parsing PIC.bg product: {product_url}")

        try:
            await page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
    
            await page.wait_for_selector('div.product-title h1', timeout=10000)

            title_element = await page.query_selector('div.product-title h1')
            title = await title_element.inner_text() if title_element else "N/A"
            if title_element:
                title = title.strip()
    
            price_element = await page.query_selector('div.price-current')
            price_text = await price_element.inner_text() if price_element else "N/A"
            if price_element:
                price_text = price_text.strip()
            price = self._extract_and_convert_price(price_text)
    
            product_data = {
                'title': title,
                'price': price,
                'url': product_url,
                'currency': self.website_currency,
                'source': 'PIC.bg',
                'source_currency': self.website_currency,
                'page': self.current_page
            }

            print(f"DEBUG: Extracted PIC.bg product: {title} - {price}")

            tech_table = await page.query_selector('table.product-details-table')
            if tech_table:
                list_items = await tech_table.query_selector_all('tr.odd, tr.even')
                for item in list_items:
                    try:
                        td_elements = await item.query_selector_all('td')
                        if len(td_elements) >= 2:
                            label_element = td_elements[0]
                            value_element = td_elements[1]
                    
                            label_text = await label_element.inner_text() if label_element else ""
                            value_text = await value_element.inner_text() if value_element else ""
                            if label_element:
                                label_text = label_text.strip()
                            if value_element:
                                value_text = value_text.strip()
                        
                            if label_text and value_text:
                                label = label_text.lower()
                                value = value_text.lower()
                        
                                if value:
                                    product_data[label] = value
                                    print(f"DEBUG: Added PIC.bg spec: {label} = {value}")
                        else:
                            print(f"DEBUG: Skipping table row with insufficient cells: {len(td_elements)}")
                    
                    except Exception as e:
                        print(f"DEBUG: Skipping invalid property: {str(e)}")
                        continue

            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing PIC.bg product page: {e}")
            return None