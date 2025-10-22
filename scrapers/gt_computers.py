import re
from turtle import title
from urllib.parse import quote, urljoin
from .base_scraper import PlaywrightBaseScraper

class GtComputersScraper(PlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://gtcomputers.bg/"
        self.exclude_keywords = [
            "Лаптоп", 'Настолен компютър', 'HP Victus', 'Acer Predator Helios'
        ]

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)
        return f"{self.base_url}search_tags/?s={encoded_term}"

    def _construct_page_url(self, base_url, search_term, page):
        if page > 1:
            return f"{self.base_url}search_tags/?s={quote(search_term)}&pg={page}"
        return base_url

    def _extract_product_links(self, page, page_url):
        """Get all product links using Playwright"""
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
            
            page.wait_for_selector('div.pt-1', timeout=10000)

            product_elements = page.query_selector_all('div.pt-1')
            print(f"DEBUG: Found {len(product_elements)} product elements")
            
            for product in product_elements:
                if self.stop_event.is_set():
                    break

                sponsored = product.query_selector('span:has-text("Sponsored")')
                if sponsored:
                    continue

                title_element = product.query_selector('a[href]')
                title = title_element.inner_text().strip() if title_element else ""
                
                if any(word.lower() in title.lower() for word in self.exclude_keywords):
                    continue

                # unavailable = product.query_selector('span.avail-old')
                # if unavailable:
                #     continue

                if title_element:
                    href = title_element.get_attribute('href')
                    if href:
                        full_url = urljoin(self.base_url, href)
                        clean_url = full_url.split('ref=')[0].split('?')[0]
                        if clean_url not in product_links:
                            product_links.append(clean_url)
                            print(f"DEBUG: Added GtComputers product: {title}")

            print(f"DEBUG: Total GtComputers product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from GtComputers: {e}")
            return []

    def _parse_product_page(self, page, product_url):
        """Extract detailed information using Playwright"""
        print(f"DEBUG: Parsing GtComputers product: {product_url}")
    
        try:
            page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
            
            page.wait_for_selector('div.sttop-mt1 h1.tit1', timeout=10000)

            title_element = page.query_selector('div.sttop-mt1 h1.tit1')
            title = title_element.inner_text().strip() if title_element else "N/A"
        
            price_element = page.query_selector('div.pr_pr')
            if price_element:
                price_text = price_element.inner_text().strip()
                bgn_part = price_text.split('/')[0].replace("Цена", "").strip()
            
                price = self._extract_gt_computers_price(bgn_part)
                if price is None:
                    price = self._extract_and_convert_price(bgn_part)
            else:
                price = 0.0
        
            product_data = {
                'title': title,
                'price': price,
                'url': product_url
            }

            print(f"DEBUG: Extracted GtComputers product: {title} - {price}")

            tech_table = page.query_selector('table.table_filter')
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
                                print(f"DEBUG: Added GtComputers spec: {label} = {value}")
                        else:
                            print(f"DEBUG: Skipping table row with insufficient cells: {len(td_elements)}")
                        
                    except Exception as e:
                        print(f"DEBUG: Skipping invalid property: {str(e)}")
                        continue

            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing GtComputers product page: {e}")
            return None