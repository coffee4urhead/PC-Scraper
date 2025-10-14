import re
from urllib.parse import urljoin, quote
from base_scraper import PlaywrightBaseScraper

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
            
            page.wait_for_selector('div#ajax-content', timeout=10000)
            
            product_elements = page.query_selector_all('div#ajax-content')
            print(f"DEBUG: Found {len(product_elements)} product elements")
            
            for product in product_elements:
                if self.stop_event.is_set():
                    break

                link_element = product.query_selector('a[href^="/products/"]')
                if link_element:
                    href = link_element.get_attribute('href')
                    if href:
                        full_url = urljoin(self.base_domain, href)
                        clean_url = full_url.split('?')[0]
                        if '/dp/' in clean_url and clean_url not in product_links:
                            product_links.append(clean_url)
                            print(f"DEBUG: Added product link: {clean_url}")

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
            
            price_whole = page.query_selector('span#price-tag')
            price_fraction = page.query_selector('sup.after-decimal')
            
            if price_whole and price_fraction:
                price_whole_text = price_whole.inner_text().strip()
                price_fraction_text = price_fraction.inner_text().strip()
                price = f"${price_whole_text}{price_fraction_text}"
            else:
                price = "N/A"
            
            product_data = {
                'title': title,
                'price': price,
                'url': product_url
            }

            ul_list = page.query_selector('ul.tech-specs-list')
            if ul_list:
                list_items = ul_list.query_selector_all('li')
                for list_item in list_items:
                    label_element = list_item.query_selector('span')
                    if label_element:
                        label = label_element.inner_text().strip().lower()
                        value = list_item.inner_text().strip()
                        product_data[label] = value

            print(f"DEBUG: Successfully parsed Ardes product: {title}")
            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing Ardes product page: {e}")
            return None