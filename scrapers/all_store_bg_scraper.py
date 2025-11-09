import re
from turtle import title
from urllib.parse import quote, urljoin
from .base_scraper import PlaywrightBaseScraper

class AllStoreScraper(PlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://allstore.bg/"

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)
        return f"{self.base_url}search.html?phrase={encoded_term}"

    def _construct_page_url(self, base_url, search_term, page):
        if page > 1:
            return f"{self.base_url}search.html?phrase={quote(search_term)}&action=dmExecAdvancedSearch&page={page}"
        return base_url

    def _extract_product_links(self, page, page_url):
        """Get all product links using Playwright"""
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
            
            page.wait_for_selector('ul.c-search-grid-page__product-grid li', timeout=10000)

            product_elements = page.query_selector_all('ul.c-search-grid-page__product-grid li')
            print(f"DEBUG: Found {len(product_elements)} product elements")
            
            for product in product_elements:
                if self.stop_event.is_set():
                    break

                sponsored = product.query_selector('span:has-text("Sponsored")')
                if sponsored:
                    continue

                title_element = product.query_selector('a.c-product-grid__product-title-link[href]')
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
                            print(f"DEBUG: Added AllStore product: {title}")

            print(f"DEBUG: Total AllStore product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from AllStore: {e}")
            return []

    def _extract_product_data(self, page, product_url):
        """Extract detailed information using Playwright"""
        print(f"DEBUG: Parsing AllStore product: {product_url}")
    
        try:
            page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
        
            page.wait_for_selector('div.c-product-page__product-name-wrapper h1', timeout=10000)

            title_element = page.query_selector('div.c-product-page__product-name-wrapper h1')
            title = title_element.inner_text().strip() if title_element else "N/A"

            price_int_element = page.query_selector('span.taxed-price-value')
            if price_int_element:
                price_int = price_int_element.inner_text().strip().replace(' лв.', '').replace('лв.', '')
    
                price_sup_element = page.query_selector('span.taxed-price-value sup')
                price_sup = price_sup_element.inner_text().strip() if price_sup_element else "00"
    
                price_elements = f"{price_int}.{price_sup}"
    
                if price_elements:
                    price = self._extract_allstore_price(price_elements)
                    print(f"DEBUG: Extracted price text: '{price_elements}' -> {price}")
                else:
                    price = 0.0
                    print("DEBUG: No price elements found")
            else:
                price = 0.0
                print("DEBUG: No price element found")
        
            product_data = {
                'title': title,
                'price': price,
                'url': product_url
            }

            print(f"DEBUG: Extracted AllStore product: {title} - {price}")
                
            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing AllStore product page: {e}")
            return None