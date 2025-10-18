import re
from urllib.parse import urljoin, quote
from .base_scraper import PlaywrightBaseScraper

class ArdesScraper(PlaywrightBaseScraper):
    def __init__(self, update_gui_callback=None):
        super().__init__(update_gui_callback)
        self.base_domain = "https://www.ardes.bg"

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)
        return f"https://www.ardes.bg/products?q={encoded_term}"

    def _construct_page_url(self, base_url, search_term, page):
        return f"{base_url}/products/page/{page}?q={quote(search_term)}"

    def _extract_product_links(self, page, page_url):
        """Get all product links using Playwright"""
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            page.goto(page_url, wait_until='domcontentloaded', timeout=30000)

            page.wait_for_selector('div.products-grid div.prod-col', timeout=10000)

            product_elements = page.query_selector_all('div.products-grid div.prod-col')
            print(f"DEBUG: Found {len(product_elements)} product elements")
        
            for i, product in enumerate(product_elements):
                if self.stop_event.is_set():
                    break

             # DEBUG: Check what links exist in each product
                print(f"DEBUG: Processing product {i+1}/{len(product_elements)}")
            
                # Try multiple link selectors
                link_selectors = [
                    'a[href^="/product/"]',
                    'a[href*="/product/"]',
                    'a.prod-link',
                    'a[href*="ardes.bg/product/"]',
                    'a'
                ]
            
                link_element = None
                for selector in link_selectors:
                    link_element = product.query_selector(selector)
                    if link_element:
                        href = link_element.get_attribute('href')
                        if href and '/product/' in href:
                            print(f"DEBUG: Found link with selector '{selector}': {href}")
                            break
                    link_element = None

                if link_element:
                    href = link_element.get_attribute('href')
                    if href:
                        full_url = urljoin(self.base_domain, href)
                        clean_url = full_url.split('?')[0]
                    
                        if '/product/' in clean_url and clean_url not in product_links:
                            product_links.append(clean_url)
                            title_element = product.query_selector('.prod-title, .title, h3, h4')
                            title = title_element.inner_text().strip() if title_element else "No Title"
                            print(f"DEBUG: Added Ardes product: {title} - {clean_url}")
                        else:
                            print(f"DEBUG: Skipping URL (not a product or duplicate): {clean_url}")
                    else:
                        print(f"DEBUG: Product {i+1} - No href found")
                else:
                    print(f"DEBUG: Product {i+1} - No link element found")
                    product_html = product.inner_html()[:200]  
                    print(f"DEBUG: Product HTML: {product_html}...")

            print(f"DEBUG: Total Ardes product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from Ardes: {e}")
            return []

    def _parse_product_page(self, page, product_url):
        """Extract detailed information using Playwright"""
        print(f"DEBUG: Parsing Ardes product: {product_url}")
    
        try:
            page.goto(product_url, wait_until='domcontentloaded', timeout=30000)

            page.wait_for_selector('div.product-title', timeout=10000)
        
            title_element = page.query_selector('div.product-title h1')
            title = title_element.inner_text().strip() if title_element else "No Title"
            price_whole = page.query_selector('span.bgn-price span.price-tag')
            price_fraction = page.query_selector('span.bgn-price sup.after-decimal')
        
            if price_whole and price_fraction:
                price_whole_text = price_whole.inner_text().strip()
                price_fraction_text = price_fraction.inner_text().strip()

                price_text = f"{price_whole_text}{price_fraction_text} лв"
                print(f"DEBUG: Combined price text: '{price_text}'")
            
                price = self._extract_and_convert_price(price_text)
            else:
                price = 0.0
                print("DEBUG: Price elements not found")
        
            product_data = {
                'title': title,
                'price': price,
                'url': product_url
            }

            print(f"DEBUG: Extracted Ardes product: {title} - {price}")

            # FIXED: Technical specs parsing
            tech_table = page.query_selector('table.table')
            if tech_table:
                list_items = tech_table.query_selector_all('tr')
                for list_item in list_items:
                    try:
                        # FIXED: Use query_selector on the row, not query_selector_all
                        label_element = list_item.query_selector('th.clmn-head')
                        value_elements = list_item.query_selector_all('td')
                    
                        if label_element and len(value_elements) >= 2:
                            label = label_element.inner_text().strip()
                            # Get the second td element (index 1) which contains the actual value
                            value_element = value_elements[1]
                            value = value_element.inner_text().strip()
                        
                            if label and value:
                                product_data[label] = value
                                print(f"DEBUG: Added property: {label} = {value}")
                    
                    except Exception as e:
                        print(f"DEBUG: Skipping invalid property: {str(e)}")
                        continue

            print(f"DEBUG: Successfully parsed Ardes product: {title}")
            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing Ardes product page: {e}")
            return None