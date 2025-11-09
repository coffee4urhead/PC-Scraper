import re
from urllib.parse import quote, urljoin
from .base_scraper import PlaywrightBaseScraper

class SeneticScraper(PlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://www.senetic.bg/"
        
    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)
        return f"{self.base_url}search/?q={encoded_term}"

    def _construct_page_url(self, base_url, search_term, page):
        if page > 1:
            return None
        return base_url

    def _extract_product_links(self, page, page_url):
        """Get all product links using Playwright"""
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
            
            page.wait_for_selector('div.listing-products__container div.product-block', timeout=10000)

            product_elements = page.query_selector_all('div.listing-products__container div.product-block')
            print(f"DEBUG: Found {len(product_elements)} product elements")
            
            for product in product_elements:
                if self.stop_event.is_set():
                    break

                sponsored = product.query_selector('span:has-text("Sponsored")')
                if sponsored:
                    continue

                title_element = product.query_selector('h3.name')
                title = title_element.inner_text().strip() if title_element else ""
                
                temp_product_data = {'title': title, 'description': ''}
                if self._should_filter_by_keywords(temp_product_data):
                    print(f'Skipped product because it was in the exclusion keywords: {self.exclude_keywords}')
                    continue

                # unavailable = product.query_selector('span.avail-old')
                # if unavailable:
                #     continue

                link_element = product.query_selector('a.product-link-events[href]')
                if link_element:
                    href = link_element.get_attribute('href')
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

    def _extract_product_data(self, page, product_url):
        """Extract detailed information using Playwright"""
        print(f"DEBUG: Parsing Senetic product: {product_url}")
    
        try:
            page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
        
            page.wait_for_selector('div.top-info__main h1.top-info__title', timeout=10000)

            title_element = page.query_selector('div.top-info__main h1.top-info__title')
            title = title_element.inner_text().strip() if title_element else "N/A"
        
            price_element = page.query_selector('div.gross-price')
            price_text = price_element.inner_text().strip() if price_element else "N/A"
            price = self._extract_and_convert_price(price_text)
        
            product_data = {
                'title': title,
                'price': price,
                'url': product_url
            }

            print(f"DEBUG: Extracted Senetic product: {title} - {price}")

            tech_table = page.query_selector('div.new-specification')
            if tech_table:
                list_items = tech_table.query_selector_all('div.features-group-row')
                for item in list_items:
                    try:
                        label = item.query_selector('div.single-feature-label').inner_text().strip()
                        value = item.query_selector('div.single-feature-value').inner_text().strip()
                        
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