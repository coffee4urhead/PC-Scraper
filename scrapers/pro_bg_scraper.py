import re
from urllib.parse import quote, urljoin
from .base_scraper import AsyncPlaywrightBaseScraper

class ProBgScraper(AsyncPlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://www.pro-bg.com/"

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)
        return f"{self.base_url}product/index.php?search_text={encoded_term}&category_id=0"

    def _construct_page_url(self, base_url, search_term, page):
        if page > 1:
            item_from = (page - 1) * 30
            return f"{self.base_url}product/index.php?category_id=0&search_text={quote(search_term)}&item_from={item_from}"
        return base_url

    def _extract_product_links(self, page, page_url):
        """Get all product links using Playwright"""
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
        
            page.wait_for_selector('div.grid-x.small-up-1', timeout=10000)

            product_elements = page.query_selector_all('div.grid-x.small-up-1 div.cell')
            print(f"DEBUG: Found {len(product_elements)} product elements")
        
            for product in product_elements:
                if self.stop_event.is_set():
                    break

                sponsored = product.query_selector('span:has-text("Sponsored")')
                if sponsored:
                    continue

                title_element = product.query_selector('div.product_box h2')
                title = title_element.inner_text().strip() if title_element else ""

                temp_product_data = {'title': title, 'description': ''}
                if self._should_filter_by_keywords(temp_product_data):
                    print(f'Skipped product because it was in the exclusion keywords: {self.exclude_keywords}')
                    continue

                link_element = (product.query_selector('div.pv_img a[href]') or 
                          product.query_selector('div.product_box a[href]') or
                          product.query_selector('h2 a[href]'))
            
                if link_element:
                    href = link_element.get_attribute('href')
                    if href:
                        full_url = urljoin(self.base_url, href)
                        clean_url = full_url.split('ref=')[0].split('?')[0]
                        if clean_url not in product_links:
                            product_links.append(clean_url)
                            print(f"DEBUG: Added Pro-bg product: {title}")

            print(f"DEBUG: Total Pro-bg product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from Pro-bg: {e}")
            return []

    def _extract_product_data(self, page, product_url):
        """Extract detailed information using Playwright"""
        print(f"DEBUG: Parsing Pro-bg product: {product_url}")
    
        try:
            page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
        
            page.wait_for_selector('div.product_box_info h2', timeout=10000)

            title_element = page.query_selector('div.product_box_info h2')
            title = title_element.inner_text().strip() if title_element else "N/A"
        
            price_container = page.query_selector('div.cell.small-12.medium-12.large-3')
            if price_container:
                price_elements = page.query_selector_all('div[style="color:#485059; font-size:18px; font-weight:700;"]')
                print(f"DEBUG: Found {len(price_elements)} price elements")
            
                if price_elements:
                    price_text = price_elements[0].inner_text().strip()
                    print(f"DEBUG: Raw price text: '{price_text}'")
                else:
                    price_text = "N/A"
            else:
                price_text = "N/A"
            
            price = float(price_text.split(" ")[0]) if price_text != "N/A" else None
            product_data = {
                'title': title,
                'price': price,
                'url': product_url
            }

            print(f"DEBUG: Extracted Pro-bg product: {title} - {price_text}")

            tech_section = page.query_selector('div.pi_desc')
            if tech_section:
                full_text = tech_section.inner_text()
            
                lines = full_text.split('\n')
            
                for line in lines:
                    line = line.strip()
                    if ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                        
                            if value and len(key) < 100:
                                product_data[key] = value
                                print(f"DEBUG: Added Pro-bg spec: {key} = {value}")

            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing Pro-bg product page: {e}")
            return None