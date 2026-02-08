import re
import asyncio
from urllib.parse import quote, urljoin
from .base_scraper import AsyncPlaywrightBaseScraper

class CyberTradeScraper(AsyncPlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://cybertrade.bg/"
        self.website_that_is_scraped = "CyberTrade.bg"
        self.update_gui_callback = update_gui_callback
        self.current_page = 1

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)
        return f"{self.base_url}product/search?search={encoded_term}"

    def _construct_page_url(self, base_url, search_term):
        if self.current_page > 1:
            return f"{self.base_url}product/search?search={quote(search_term)}&page={self.current_page}"
        return base_url

    async def _extract_product_links(self, page, page_url):
        """Get all product links using Playwright"""
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            await page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
            
            await page.wait_for_selector('div.row div.product-list', timeout=10000)

            product_elements = await page.query_selector_all('div.row div.product-list')
            print(f"DEBUG: Found {len(product_elements)} product elements")
            
            for product in product_elements:
                if self._stop_event.is_set():
                    break

                sponsored = await product.query_selector('span:has-text("Sponsored")')
                if sponsored:
                    continue

                title_element = await product.query_selector('a[href] span')
                title = ""
                if title_element:
                    title_text = await title_element.inner_text()
                    title = title_text.strip()
                
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
                        if clean_url not in product_links:
                            product_links.append(clean_url)
                            print(f"DEBUG: Added CyberTrade product: {title}")

            print(f"DEBUG: Total CyberTrade product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from CyberTrade: {e}")
            return []

    async def _extract_price_from_page(self, page):
        """Extract price from CyberTrade page"""
        price_element = await page.query_selector('span.update_price')
        if price_element:
            price_text = await price_element.inner_text()
            price_text = price_text.strip()
        
            print(f"DEBUG: Raw price text: '{price_text}'")
        
            if '|' in price_text:
                parts = price_text.split('|')
                for part in parts:
                    if 'лв.' in part or 'BGN' in part.lower():
                        price_text = part.strip()
                        print(f"DEBUG: Selected BGN price part: '{price_text}'")
                        break
                else:
                    price_text = parts[0].strip()
                    print(f"DEBUG: No BGN found, using first part: '{price_text}'")
        
            try:
                clean_price = re.sub(r'[^\d.,]', '', price_text)
            
                print(f"DEBUG: After cleaning non-numeric: '{clean_price}'")
            
                if ',' in clean_price and '.' in clean_price:
                    clean_price = clean_price.replace('.', '').replace(',', '.')
                    print(f"DEBUG: After handling both separators: '{clean_price}'")
                elif ',' in clean_price:
                    clean_price = clean_price.replace(',', '.')
                    print(f"DEBUG: After replacing comma: '{clean_price}'")
            
                clean_price = re.sub(r'[^\d.]', '', clean_price)
            
                print(f"DEBUG: Final cleaned price: '{clean_price}'")
            
                if clean_price:
                    price = float(clean_price)
                    print(f"DEBUG: Successfully converted to float: {price}")
                    return price
                else:
                    print(f"DEBUG: Empty price after cleaning")
                    return 0.0
                
            except ValueError as e:
                print(f"DEBUG: Could not convert price '{clean_price}': {e}")
                return 0.0
            except Exception as e:
                print(f"DEBUG: Error processing price: {e}")
                return 0.0
    
        print(f"DEBUG: No price element found")
        return 0.0

    async def _extract_product_data(self, page, product_url):
        """Extract detailed information using Playwright"""
        print(f"DEBUG: Parsing CyberTrade product: {product_url}")
    
        try:
            await page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
        
            await page.wait_for_selector('div#product h1.product-title', timeout=10000)

            title_element = await page.query_selector('div#product h1.product-title')
            title = ""
            if title_element:
                title_text = await title_element.inner_text()
                title = title_text.strip()
            else:
                title = "N/A"
        
            price = await self._extract_price_from_page(page)
        
            product_data = {
                'title': title,
                'price': price,
                'url': product_url,
                'currency': self.website_currency,
                'source': 'Allstore.bg',  
                'source_currency': self.website_currency,
                'page': self.current_page
            }

            print(f"DEBUG: Extracted CyberTrade product: {title} - {price} лв.")

            tech_table = await page.query_selector('table.table, table.table-hover')
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
                                print(f"DEBUG: Added CyberTrade spec: {label} = {value}")
                        else:
                            print(f"DEBUG: Skipping table row with insufficient cells: {len(td_elements)}")
                        
                    except Exception as e:
                        print(f"DEBUG: Skipping invalid property: {str(e)}")
                        continue

            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing CyberTrade product page: {e}")
            return None