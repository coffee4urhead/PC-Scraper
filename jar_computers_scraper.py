import re
from urllib.parse import quote, urljoin
from base_scraper import PlaywrightBaseScraper

class JarComputersScraper(PlaywrightBaseScraper):
    def __init__(self, update_gui_callback=None):
        super().__init__(update_gui_callback)
        self.base_url = "https://www.jarcomputers.com/"
        self.exclude_keywords = [
            "Лаптоп", 'Настолен компютър', 'HP Victus', 'Acer Predator Helios'
        ]

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)
        return f"{self.base_url}search?q={encoded_term}"

    def _construct_page_url(self, base_url, search_term, page):
        if page > 1:
            return f"{self.base_url}search?q={quote(search_term)}&ref=&page={page}"
        return base_url

    def _extract_product_links(self, page, page_url):
        """Get all product links using Playwright"""
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            # Navigate to the search page
            page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
            
            # Wait for product list to load
            page.wait_for_selector('ol#product_list', timeout=10000)
            
            # Get all product elements
            product_elements = page.query_selector_all('ol#product_list li[class*="sProduct"]')
            print(f"DEBUG: Found {len(product_elements)} product elements")
            
            for product in product_elements:
                if self.stop_event.is_set():
                    break

                # Check for sponsored products
                sponsored = product.query_selector('span:has-text("Sponsored")')
                if sponsored:
                    continue

                # Get title for exclusion check
                title_element = product.query_selector('span.short_title.fn')
                title = title_element.inner_text().strip() if title_element else ""
                
                # Check if product should be excluded
                if any(word.lower() in title.lower() for word in self.exclude_keywords):
                    continue

                # Check availability
                unavailable = product.query_selector('span.avail-old')
                if unavailable:
                    continue

                # Get product link
                link_element = product.query_selector('a[href]')
                if link_element:
                    href = link_element.get_attribute('href')
                    if href:
                        full_url = urljoin(self.base_url, href)
                        clean_url = full_url.split('ref=')[0].split('?')[0]
                        if clean_url not in product_links:
                            product_links.append(clean_url)
                            print(f"DEBUG: Added JarComputers product: {title}")

            print(f"DEBUG: Total JarComputers product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from JarComputers: {e}")
            return []

    def _parse_product_page(self, page, product_url):
        """Extract detailed information using Playwright"""
        print(f"DEBUG: Parsing JarComputers product: {product_url}")
        
        try:
            # Navigate to product page
            page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
            
            # Wait for key elements
            page.wait_for_selector('div#product_name', timeout=10000)
            
            # Extract title
            title_element = page.query_selector('div#product_name h1')
            title = title_element.inner_text().strip() if title_element else "N/A"
            
            # Extract price
            price_element = page.query_selector('div.price')
            price = price_element.inner_text().strip().replace("лв", "").strip() if price_element else "N/A"
            
            product_data = {
                'title': title,
                'price': price,
                'url': product_url
            }

            print(f"DEBUG: Extracted JarComputers product: {title} - {price}")

            # Extract technical specifications
            tech_table = page.query_selector('ul.pprop')
            if tech_table:
                list_items = tech_table.query_selector_all('li')
                for item in list_items:
                    try:
                        label = item.inner_text().strip().lower()
                        value_element = item.query_selector('b')
                        if value_element:
                            value = value_element.inner_text().strip()
                            product_data[label] = value
                            print(f"DEBUG: Added JarComputers spec: {label} = {value}")
                    except Exception as e:
                        print(f"DEBUG: Skipping invalid property: {str(e)}")
                        continue

            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing JarComputers product page: {e}")
            return None