import re
from urllib.parse import quote, urljoin
from .base_scraper import AsyncPlaywrightBaseScraper

class AllStoreScraper(AsyncPlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://allstore.bg/"
        self.current_page = 1
        self.update_gui_callback = update_gui_callback
        self.website_that_is_scraped = "AllStore.bg"

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)
        return f"{self.base_url}search.html?phrase={encoded_term}"

    def _construct_page_url(self, base_url, search_term):
        if self.current_page >= 1:
            return f"{self.base_url}search.html?phrase={quote(search_term)}&action=dmExecAdvancedSearch&page={self.current_page}"
        return base_url

    async def _extract_product_links(self, page, page_url):
        """Get all product links using Playwright"""
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            await page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
            
            await page.wait_for_selector('ul.c-search-grid-page__product-grid li', timeout=10000)

            product_elements = await page.query_selector_all('ul.c-search-grid-page__product-grid li')
            if product_elements:
                print(f"DEBUG: Found {len(product_elements)} product elements")
            
            for product in product_elements:
                if self._stop_event.is_set():
                    break

                sponsored = await product.query_selector('span:has-text("Sponsored")')
                if sponsored:
                    continue

                title_element = await product.query_selector('a.c-product-grid__product-title-link[href]')
                
                title = ""
                if title_element:
                    title = await title_element.inner_text()
                    title = title.strip() if title else "N/A"
                else:
                    title = "N/A"
                    
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
                            print(f"DEBUG: Added AllStore product: {title}")

            print(f"DEBUG: Total AllStore product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from AllStore: {e}")
            return [] 

    async def _extract_product_data(self, page, product_url):
        """Extract detailed information using Playwright"""
        print(f"DEBUG: Parsing AllStore product: {product_url}")
    
        try:
            await page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
        
            await page.wait_for_selector('div.c-product-page__product-name-wrapper h1', timeout=10000)

            title_element = await page.query_selector('div.c-product-page__product-name-wrapper h1')
            title = ""
            if title_element:
                title = await title_element.inner_text()
                title = title.strip()
            else:
                title = "N/A"

            price_int_element = await page.query_selector('span.taxed-price-value')
            price = 0.0
            
            if price_int_element:
                price_int_text = await price_int_element.inner_text()
                price_int_text = price_int_text.replace('€', '')

                price_lines = price_int_text.strip().split('\n')
                if price_lines:
                    price_int = price_lines[0].strip()  
                else:
                    price_int = "0"

                price_sup_element = await page.query_selector('span.taxed-price-value sup')
                price_sup = "00"
                if price_sup_element:
                    price_sup_text = await price_sup_element.inner_text()
                    price_sup = price_sup_text.strip()
    
                price_text = f"{price_int}.{price_sup}"
    
                if price_text:
                    print(f"price text is {price_text}")
                    price = ''.join(price_text.split('\n')).replace("€", '')
                    print(f"DEBUG: Extracted price text: '{price_text}' -> {price}")
                else:
                    print("DEBUG: No price elements found")
            else:
                print("DEBUG: No price element found")
        
            product_data = {
                'title': title,
                'price': price,
                'url': product_url,
                'currency': self.website_currency,
                'source': self.website_that_is_scraped,  
                'source_currency': self.website_currency,
                'page': self.current_page
            }

            print(f"DEBUG: Extracted AllStore product: {title} - {price}")
                
            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing AllStore product page: {e}")
            return None  