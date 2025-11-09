import re
from urllib.parse import quote, urljoin
from .base_scraper import PlaywrightBaseScraper

class CyberTradeScraper(PlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://cybertrade.bg/"

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)
        return f"{self.base_url}product/search?search={encoded_term}"

    def _construct_page_url(self, base_url, search_term, page):
        if page > 1:
            return f"{self.base_url}product/search?search={quote(search_term)}&page={page}"
        return base_url

    def _extract_product_links(self, page, page_url):
        """Get all product links using Playwright"""
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
            
            page.wait_for_selector('div.row div.product-list', timeout=10000)

            product_elements = page.query_selector_all('div.row div.product-list')
            print(f"DEBUG: Found {len(product_elements)} product elements")
            
            for product in product_elements:
                if self.stop_event.is_set():
                    break

                sponsored = product.query_selector('span:has-text("Sponsored")')
                if sponsored:
                    continue

                title_element = product.query_selector('a[href] span')
                title = title_element.inner_text().strip() if title_element else ""
                
                temp_product_data = {'title': title, 'description': ''}

                if self._should_filter_by_keywords(temp_product_data):
                    print(f'Skipped product because it was in the exclusion keywords: {self.exclude_keywords}')
                    continue

                # unavailable = product.query_selector('span.avail-old')
                # if unavailable:
                #     continue

                link_element = product.query_selector('a[href]')
                if link_element:
                    href = link_element.get_attribute('href')
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

    def _extract_product_data(self, page, product_url):
        """Extract detailed information using Playwright"""
        print(f"DEBUG: Parsing CyberTrade product: {product_url}")
    
        try:
            page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
        
            page.wait_for_selector('div#product h1.product-title', timeout=10000)

            title_element = page.query_selector('div#product h1.product-title')
            title = title_element.inner_text().strip() if title_element else "N/A"
        
            price_element = page.query_selector('span.update_price')
            price_text = price_element.inner_text().strip() if price_element else "N/A"
            price = self._extract_and_convert_price(price_text)
        
            product_data = {
                'title': title,
                'price': price,
                'url': product_url
            }

            print(f"DEBUG: Extracted CyberTrade product: {title} - {price}")

            tech_table = page.query_selector('table.table, table.table-hover')
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