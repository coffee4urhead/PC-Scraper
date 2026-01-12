import re
from urllib.parse import quote, urljoin
from .base_scraper import AsyncPlaywrightBaseScraper

class OptimalComputersScraper(AsyncPlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://optimal-computers.bg/"

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)
        return f"{self.base_url}products/search?s={encoded_term}"

    def _construct_page_url(self, base_url, search_term, page):
        """
        Optimal Computers doesn't use pagination - all results are on one page.
        Return the base URL for all page requests.
        """
        if page == 1:
            return base_url
        else:
            print(f"DEBUG: Optimal Computers - no pagination, stopping at page 1")
            return None
    
    def _extract_product_links(self, page, page_url):
        """Get all product links using Playwright"""
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
            
            page.wait_for_selector('div.cards--products', timeout=10000)

            product_elements = page.query_selector_all('div.cards--products div.product')
            print(f"DEBUG: Found {len(product_elements)} product elements")
            
            for product in product_elements:
                if self.stop_event.is_set():
                    break

                sponsored = product.query_selector('span:has-text("Sponsored")')
                if sponsored:
                    continue

                title_element = product.query_selector('a.link--inherit')
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
                            print(f"DEBUG: Added Optimal Computers product: {title}")

            print(f"DEBUG: Total Optimal Computers product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from Optimal Computers: {e}")
            return []

    def _extract_product_data(self, page, product_url):
        """Extract detailed information using Playwright"""
        print(f"DEBUG: Parsing Optimal Computers product: {product_url}")
    
        try:
            page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
        
            page.wait_for_selector('div.page-header h1', timeout=10000)

            title_element = page.query_selector('div.page-header h1')
            title = title_element.inner_text().strip() if title_element else "N/A"
        
            price_element = page.query_selector('span.product-price')
            price_text = price_element.inner_text().strip() if price_element else "N/A"
            price = float(price_text.split(" / ")[0].replace("лв.", "").replace(" ", '').strip()) 
        
            product_data = {
                'title': title,
                'price': price / 100,
                'url': product_url
            }

            print(f"DEBUG: Extracted Optimal Computers product: {title} - {price}")

            tech_table = page.query_selector('ul.product-characteristics')
            if tech_table:
                list_items = tech_table.query_selector_all('li')
                for item in list_items:
                    try:
                        label_element = item.query_selector('div.element--color-light')
                        if label_element:
                            label_text = label_element.inner_text().strip()
                        
                            full_text = item.inner_text().strip()
                        
                            value_text = full_text.replace(label_text, '').strip()
                        
                            value_text = value_text.lstrip(':').strip()
                        
                            if label_text and value_text:
                                product_data[label_text] = value_text
                                print(f"DEBUG: Added Optimal Computers spec: {label_text} = {value_text}")
                        else:
                            print(f"DEBUG: No label found in list item")
                        
                    except Exception as e:
                        print(f"DEBUG: Skipping invalid property: {str(e)}")
                        continue

            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing Optimal Computers product page: {e}")
            return None