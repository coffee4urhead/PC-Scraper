import re
from urllib.parse import quote, urljoin
from .base_scraper import PlaywrightBaseScraper

class PICBgScraper(PlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://www.pic.bg/"
        self.exclude_keywords = [
            "Лаптоп", 'Настолен компютър', 'HP Victus', 'Acer Predator Helios'
        ]

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)
        return f"{self.base_url}search/{encoded_term}"

    def _construct_page_url(self, base_url, search_term, page):
        if page > 1:
            return f"{self.base_url}search/{quote(search_term)}/filter/page/{page}"
        return base_url

    def _extract_product_links(self, page, page_url):
        """Get all product links using Playwright - corrected for actual HTML structure"""
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
        
            page.wait_for_selector('div.res-page', timeout=10000)

            results_container = page.query_selector('div.res-page')
            if not results_container:
                print("DEBUG: No results container found")
                return []

            product_elements = results_container.query_selector_all('div.product-item-holder-new')
            print(f"DEBUG: Found {len(product_elements)} product-item-holder-new elements")
        
            for i, product in enumerate(product_elements):
                if self.stop_event.is_set():
                    break

                print(f"DEBUG: Processing product {i+1}/{len(product_elements)}")
            
                sponsored = product.query_selector('span:has-text("Sponsored"), div:has-text("Sponsored")')
                if sponsored:
                    print(f"DEBUG: Product {i+1} is sponsored, skipping")
                    continue

                title_element = product.query_selector('span.ttl, .product-title, .title, a[href] span')
                title = title_element.inner_text().strip() if title_element else ""
                print(f"DEBUG: Product {i+1} title: '{title}'")
            
                if title and any(word.lower() in title.lower() for word in self.exclude_keywords):
                    print(f"DEBUG: Product {i+1} excluded by keywords: '{title}'")
                    continue

                link_element = product.query_selector('a[href]')
                if link_element:
                    href = link_element.get_attribute('href')
                    if href:
                        full_url = urljoin(self.base_url, href)
                        clean_url = full_url.split('ref=')[0].split('?')[0]
                        product_links.append(clean_url)
                        print(f"DEBUG: Added PIC.bg product: '{title}' -> {clean_url}")
                else:
                    print(f"DEBUG: Product {i+1} has no link element")

            print(f"DEBUG: Total PIC.bg product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from PIC.bg: {e}")
            return []

    def _parse_product_page(self, page, product_url):
        """Extract detailed information using Playwright"""
        print(f"DEBUG: Parsing PIC.bg product: {product_url}")

        try:
            page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
    
            page.wait_for_selector('div.product-title h1', timeout=10000)

            title_element = page.query_selector('div.product-title h1')
            title = title_element.inner_text().strip() if title_element else "N/A"
    
            price_element = page.query_selector('div.price-holder')
            price_text = price_element.inner_text().strip() if price_element else "N/A"
            price = self._extract_and_convert_price(price_text)
    
            product_data = {
                'title': title,
                'price': price,
                'url': product_url
            }

            print(f"DEBUG: Extracted PIC.bg product: {title} - {price}")

            tech_table = page.query_selector('table.product-details-table')
            if tech_table:
                list_items = tech_table.query_selector_all('tr.odd, tr.even')
                for item in list_items:
                    try:
                        td_elements = item.query_selector_all('td')
                        if len(td_elements) >= 2:
                            label_element = td_elements[0]
                            value_element = td_elements[1]
                    
                            label_text = label_element.inner_text().strip() if label_element else ""
                            value_text = value_element.inner_text().strip() if value_element else ""
                        
                            if label_text and value_text:
                                label = label_text.lower()
                                value = value_text.lower()
                        
                                if value:
                                    product_data[label] = value
                                    print(f"DEBUG: Added PIC.bg spec: {label} = {value}")
                        else:
                            print(f"DEBUG: Skipping table row with insufficient cells: {len(td_elements)}")
                    
                    except Exception as e:
                        print(f"DEBUG: Skipping invalid property: {str(e)}")
                        continue

            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing PIC.bg product page: {e}")
            return None