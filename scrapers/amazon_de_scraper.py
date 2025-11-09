import re
from urllib.parse import quote, urljoin
from .base_scraper import PlaywrightBaseScraper

class AmazonDeScraper(PlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://www.amazon.de/"

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)
        return f"{self.base_url}s?k={encoded_term}&crid=2J0PCSZU19ONB&sprefix={encoded_term}%2Caps%2C153&ref=nb_sb_noss_2"

    def _construct_page_url(self, base_url, search_term, page):
        if page > 1:
            return f"{self.base_url}s?k={quote(search_term)}&page=2&xpid=L1vzNrANz4x19&crid=2J0PCSZU19ONB&qid=1760797196&sprefix={quote(search_term)}%2Caps%2C153&ref=sr_pg_2"
        return base_url

    def _extract_product_links(self, page, page_url):
        """Get all product links using Playwright"""
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
        
            page.wait_for_selector('div[data-component-type="s-impression-counter"]', timeout=10000)

            product_elements = page.query_selector_all('div[data-component-type="s-search-result"]')
            print(f"DEBUG: Found {len(product_elements)} product elements")
        
            for i, product in enumerate(product_elements):
                if self.stop_event.is_set():
                    break

                print(f"DEBUG: Processing product {i+1}/{len(product_elements)}")
            
                sponsored = product.query_selector('span:has-text("Sponsored")')
                if sponsored:
                    print(f"DEBUG: Product {i+1} - Skipping sponsored")
                    continue

                title_element = product.query_selector('div[data-cy=title-recipe]')
                if title_element:
                    title = title_element.inner_text().strip()
                else:
                    print(f"DEBUG: Product {i+1} - No title found")
                    continue

                print(f"DEBUG: Product {i+1} - Title: '{title}'")
            
                temp_product_data = {'title': title, 'description': ''}
                if self._should_filter_by_keywords(temp_product_data):
                    print(f'Skipped product because it was in the exclusion keywords: {self.exclude_keywords}')
                    continue

                link_element = product.query_selector('a.a-link-normal')
                if link_element:
                    href = link_element.get_attribute('href')
                    if href and '/dp/' in href:  
                        full_url = urljoin(self.base_url, href)
                        clean_url = full_url.split('ref=')[0].split('?')[0]
                        if clean_url not in product_links:
                            product_links.append(clean_url)
                            print(f"DEBUG: Added Amazon.de product: {title}")
                    else:
                        print(f"DEBUG: Product {i+1} - Not a product link: {href}")
                else:
                    print(f"DEBUG: Product {i+1} - No link element found")

            print(f"DEBUG: Total Amazon.de product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from Amazon.de: {e}")
            return []

    def _extract_product_data(self, page, product_url):
        """Extract detailed information using Playwright"""
        print(f"DEBUG: Parsing Amazon.de product: {product_url}")

        try:
            page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
    
            page.wait_for_selector('h1#title span#productTitle', timeout=10000)

            title_element = page.query_selector('h1#title span#productTitle')
            title = title_element.inner_text().strip() if title_element else "N/A"
    
            price_element_whole = page.query_selector('span.a-price-whole')
            price_element_fraction = page.query_selector('span.a-price-fraction')
        
            if price_element_whole and price_element_fraction:
                whole_part = price_element_whole.inner_text().strip()
                fraction_part = price_element_fraction.inner_text().strip()
                price_text = f"${whole_part}.{fraction_part}"
            else:
                price_text = "N/A"
            
            price = self._extract_and_convert_price(price_text)
    
            product_data = {
                'title': title,
                'price': price,
                'url': product_url
            }

            print(f"DEBUG: Extracted Amazon.de product: {title} - {price}")

            tech_table = page.query_selector('table[role=list]')
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
                                print(f"DEBUG: Added Amazon.de spec: {label} = {value}")
                        else:
                            print(f"DEBUG: Skipping table row with insufficient cells: {len(td_elements)}")
                    
                    except Exception as e:
                        print(f"DEBUG: Skipping invalid property: {str(e)}")
                        continue

            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing Amazon.de product page: {e}")
            return None