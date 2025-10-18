import re
from urllib.parse import quote, urljoin
from .base_scraper import PlaywrightBaseScraper

class DesktopScraper(PlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://desktop.bg/"
        self.exclude_keywords = [
            "Лаптоп", 'Настолен компютър', 'HP Victus', 'Acer Predator Helios'
        ]

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)
        return f"{self.base_url}search?q={encoded_term}"

    def _construct_page_url(self, base_url, search_term, page):
        if page > 1:
            return f"{self.base_url}search?page={page}&q={quote(search_term)}"
        return base_url

    def _extract_product_links(self, page, page_url):
        """Get all product links from a specific search results page using Playwright"""
        product_links = []
        print(f"DEBUG: _extract_product_links called for: {page_url}")

        try:
            print(f"DEBUG: Navigating to search page...")
            page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
            
            print("DEBUG: Waiting for products list...")
            page.wait_for_selector('ul.products', timeout=10000)
            
            product_elements = page.query_selector_all('ul.products li[id^="product_"]')
            print(f"DEBUG: Found {len(product_elements)} product elements")
            
            for product in product_elements:
                if self.stop_event.is_set():
                    break

                link_element = product.query_selector('a[href]')
                if link_element:
                    href = link_element.get_attribute('href')
                    if href:
                        full_url = urljoin(self.base_url, href)
                        clean_url = full_url.split('ref=')[0].split('?')[0]
                        if clean_url not in product_links:
                            product_links.append(clean_url)
                            print(f"DEBUG: Added product link: {clean_url}")

            print(f"DEBUG: Total product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links: {e}")
            try:
                page.screenshot(path=f"debug_error_{page_url.split('/')[-1]}.png")
            except:
                pass
            return []

    def _parse_product_page(self, page, product_url):
        """Extract detailed information from a product page using Playwright"""
        print(f"DEBUG: _parse_product_page called for: {product_url}")
        
        try:
            page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
            
            page.wait_for_selector('div#content', timeout=10000)
            
            title_element = page.query_selector('div#content h1[itemprop="name"]')
            title = title_element.inner_text().strip() if title_element else "N/A"
            
            price_element = page.query_selector('span[itemprop="price"]')
            price = price_element.inner_text().strip().replace("лв", "").strip() if price_element else "N/A"
            
            product_data = {
                'title': title,
                'price': price,
                'url': product_url
            }

            print(f"DEBUG: Extracted product: {title} - {price}")

            tech_table = page.query_selector('table.product-characteristics')
            if tech_table:
                rows = tech_table.query_selector_all('tr')
                
                for row in rows:
                    try:
                        label_element = row.query_selector('th[scope="row"]')
                        value_element = row.query_selector('td')
                        
                        if label_element and value_element:
                            label = label_element.inner_text().strip().lower()
                            
                            if label == "описание":
                                continue
                            else:
                                value = value_element.inner_text().strip().lower()
                                product_data[label] = value
                                print(f"DEBUG: Added spec: {label} = {value}")

                    except Exception as e:
                        print(f"DEBUG: Skipping invalid property: {str(e)}")
                        continue

            return product_data

        except Exception as e:
            print(f"DEBUG: Product page error: {str(e)}")
            return None