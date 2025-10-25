import re
from urllib.parse import quote, urljoin
from .base_scraper import PlaywrightBaseScraper

class PcTechBgScraper(PlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://www.pctech.bg/"
        self.exclude_keywords = [
            "Лаптоп", 'Настолен компютър', 'HP Victus', 'Acer Predator Helios'
        ]

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)
        return f"{self.base_url}index.php?route=product/search&search={encoded_term}"

    def _construct_page_url(self, base_url, search_term, page):
        if page > 1:
            return f"{self.base_url}index.php?route=product/search&search={search_term}&page={page}"
        return base_url

    def _extract_product_links(self, page, page_url):
        """Get all product links using Playwright"""
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
            
            page.wait_for_selector('div.flex_height_row div.product-layout', timeout=10000)

            product_elements = page.query_selector_all('div.flex_height_row div.product-layout')
            print(f"DEBUG: Found {len(product_elements)} product elements")
            
            for product in product_elements:
                if self.stop_event.is_set():
                    break

                sponsored = product.query_selector('span:has-text("Sponsored")')
                if sponsored:
                    continue

                title_element = product.query_selector('div.product-name a[href]')
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
                            print(f"DEBUG: Added PcTech.bg product: {title}")

            print(f"DEBUG: Total PcTech.bg product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from PcTech.bg: {e}")
            return []

    def _parse_product_page(self, page, product_url):
        """Extract detailed information using Playwright"""
        print(f"DEBUG: Parsing PcTech.bg product: {product_url}")
    
        try:
            page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
        
            page.wait_for_selector('div.col-xs-12 h1.pr_h1', timeout=10000)

            title_element = page.query_selector('div.col-xs-12 h1.pr_h1')
            title = title_element.inner_text().strip() if title_element else "N/A"
        
            price_element = page.query_selector('span.autocalc-product-price')
            price_text = price_element.inner_text().strip() if price_element else "N/A"
            price = float(price_text.split(".")[0].replace("лв", "").replace(",", ".").strip()) if price_text != "N/A" else None
        
            product_data = {
                'title': title,
                'price': price,
                'url': product_url
            }

            print(f"DEBUG: Extracted PcTech.bg product: {title} - {price}")

            tech_table = page.query_selector('table.product_specification')
            if tech_table:
                list_items = tech_table.query_selector_all('tr')
                for item in list_items:
                    try:
                        label = item.query_selector('td.product_specification_title span').inner_text().strip()
                        value = item.query_selector('td.product_specification_value').inner_text().strip()
                        product_data[label] = value
                        print(f"DEBUG: Added property - {label}: {value}")
                    except Exception as e:
                        print(f"DEBUG: Skipping invalid property: {str(e)}")
                        continue

            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing PcTech.bg product page: {e}")
            return None