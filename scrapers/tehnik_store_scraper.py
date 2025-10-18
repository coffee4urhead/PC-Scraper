import re
from urllib.parse import quote, urljoin
from .base_scraper import PlaywrightBaseScraper

class TehnikStoreScraper(PlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://tehnik.store/"
        self.exclude_keywords = [
            "Лаптоп", 'Настолен компютър', 'HP Victus', 'Acer Predator Helios'
        ]

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)
        return f"{self.base_url}?s={encoded_term}&product_cat=0&post_type=product"

    def _construct_page_url(self, base_url, search_term, page):
        if page > 1:
            item_from = (page - 1) * 30
            return f"{self.base_url}?s={quote(search_term)}&product_cat=0&post_type=product&orderby=relevance&app={item_from}"
        return base_url

    def _extract_product_links(self, page, page_url):
        """Get all product links using Playwright"""
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
            
            page.wait_for_selector('div.products', timeout=10000)

            product_elements = page.query_selector_all('div.products div.product')
            print(f"DEBUG: Found {len(product_elements)} product elements")
            
            for product in product_elements:
                if self.stop_event.is_set():
                    break

                sponsored = product.query_selector('span:has-text("Sponsored")')
                if sponsored:
                    continue

                title_element = product.query_selector('h2.woocommerce-loop-product__title')
                title = title_element.inner_text().strip() if title_element else ""
                
                if any(word.lower() in title.lower() for word in self.exclude_keywords):
                    continue

                # unavailable = product.query_selector('span.avail-old')
                # if unavailable:
                #     continue

                link_element = product.query_selector('a.woocommerce-LoopProduct-link[href]')
                if link_element:
                    href = link_element.get_attribute('href')
                    if href:
                        full_url = urljoin(self.base_url, href)
                        clean_url = full_url.split('ref=')[0].split('?')[0]
                        if clean_url not in product_links:
                            product_links.append(clean_url)
                            print(f"DEBUG: Added TehnikStore product: {title}")

            print(f"DEBUG: Total TehnikStore product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from TehnikStore: {e}")
            return []

    def _parse_product_page(self, page, product_url):
        """Extract detailed information using Playwright"""
        print(f"DEBUG: Parsing TehnikStore product: {product_url}")

        try:
            page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
    
            page.wait_for_selector('div.single-product-header h1.product_title', timeout=10000)

            title_element = page.query_selector('div.single-product-header h1.product_title')
            title = title_element.inner_text().strip() if title_element else "N/A"

            # DEBUG: Check what price elements exist on the page
            print("DEBUG: Searching for price elements...")
        
            # Try multiple price selectors
            price_selectors = [
                'p.price',
                '.price',
                'span.price',
                'ins .woocommerce-Price-amount',
                'del .woocommerce-Price-amount',
                '.woocommerce-Price-amount',
                'span.amount',
                'bdi'
            ]
        
            price_text = "N/A"
        
            for selector in price_selectors:
                elements = page.query_selector_all(selector)
                print(f"DEBUG: Selector '{selector}' found {len(elements)} elements")
            
                for i, elem in enumerate(elements):
                    text = elem.inner_text().strip()
                    html = elem.inner_html()
                    print(f"DEBUG:   Element {i}: text='{text}', html='{html[:100]}...'")
                
                    # If we find something that looks like a price, use it
                    if any(currency in text for currency in ['лв', '€', '$']) and any(char.isdigit() for char in text):
                        price_text = text
                        print(f"DEBUG:   -> Using this as price: '{price_text}'")
                        break
                if price_text != "N/A":
                    break
        
            # If still no price found, try to get the entire price section
            if price_text == "N/A":
                price_section = page.query_selector('p.price')
                if price_section:
                    full_price_html = price_section.inner_html()
                    full_price_text = price_section.inner_text()
                    print(f"DEBUG: Full price section HTML: {full_price_html}")
                    print(f"DEBUG: Full price section text: {full_price_text}")
                
                    price_matches = re.findall(r'(\d+[.,]\d+)\s*лв', full_price_text)
                    if price_matches:
                        price_text = f"{price_matches[0]} лв."
                        print(f"DEBUG: Regex extracted price: '{price_text}'")
        
            print(f"DEBUG: Final price text to process: '{price_text}'")
            price = self._extract_and_convert_price(price_text)
    
            product_data = {
                'title': title,
                'price': price,
                'url': product_url
            }

            print(f"DEBUG: Extracted TehnikStore product: {title} - {price}")

            # Extract specifications
            tech_section = page.query_selector('div.woocommerce-Tabs-panel')
            if tech_section:
                # Try to find specification tables or lists
                spec_rows = tech_section.query_selector_all('tr')
                if spec_rows:
                    # It's a table format
                    for row in spec_rows:
                        try:
                            cells = row.query_selector_all('td')
                            if len(cells) >= 2:
                                key = cells[0].inner_text().strip()
                                value = cells[1].inner_text().strip()
                                if key and value:
                                    product_data[key] = value
                                    print(f"DEBUG: Added spec (table): {key} = {value}")
                        except Exception as e:
                            print(f"DEBUG: Skipping table row: {str(e)}")
                else:
                    # Try list items
                    list_items = tech_section.query_selector_all('li')
                    for item in list_items:
                        try:
                            text = item.inner_text().strip()
                            if ':' in text:
                                parts = text.split(':', 1)
                                if len(parts) == 2:
                                    key = parts[0].strip()
                                    value = parts[1].strip()
                                    if key and value:
                                        product_data[key] = value
                                        print(f"DEBUG: Added spec (list): {key} = {value}")
                        except Exception as e:
                            print(f"DEBUG: Skipping list item: {str(e)}")

            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing TehnikStore product page: {e}")
            return None