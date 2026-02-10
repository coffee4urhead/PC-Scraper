import re
from urllib.parse import quote, urljoin
from .base_scraper import AsyncPlaywrightBaseScraper

class PcTechBgScraper(AsyncPlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://www.pctech.bg/"
        self.current_page = 1
        self.update_gui_callback = update_gui_callback
        self.website_that_is_scraped = "PcTech.bg"

    def _get_base_url(self, search_term):
        encoded_term = quote(search_term)
        return f"{self.base_url}index.php?route=product/search&search={encoded_term}"

    def _construct_page_url(self, base_url, search_term):
        if self.current_page > 1:
            return f"{self.base_url}index.php?route=product/search&search={search_term}&page={self.current_page}"
        return base_url

    async def _extract_product_links(self, page, page_url):
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            await page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
            
            await page.wait_for_selector('div.flex_height_row div.product-layout', timeout=10000)

            product_elements = await page.query_selector_all('div.flex_height_row div.product-layout')
            print(f"DEBUG: Found {len(product_elements)} product elements")
            
            for product in product_elements:
                if self._stop_event.is_set():
                    break

                sponsored = await product.query_selector('span:has-text("Sponsored")')
                if sponsored:
                    continue

                title_element = await product.query_selector('div.product-name a[href]')
                title = await title_element.inner_text() if title_element else ""
                if title_element:
                    title = title.strip()
                
                temp_product_data = {'title': title, 'description': ''}
                if self._should_filter_by_keywords(temp_product_data):
                    print(f'Skipped product because it was in the exclusion keywords: {self.exclude_keywords}')
                    continue

                if title_element:
                    href = await title_element.get_attribute('href')
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

    async def _extract_product_data(self, page, product_url):
        print(f"DEBUG: Parsing PcTech.bg product: {product_url}")
    
        try:
            await page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
        
            await page.wait_for_selector('div.col-xs-12 h1.pr_h1', timeout=10000)

            title_element = await page.query_selector('div.col-xs-12 h1.pr_h1')
            title = await title_element.inner_text() if title_element else "N/A"
            if title_element:
                title = title.strip()
        
            price_element = await page.query_selector('span.autocalc-product-price')
            price_text = await price_element.inner_text() if price_element else "N/A"
            if price_element:
                price_text = price_text.strip()
            
            price = None
            if price_text != "N/A":
                try:
                    match = re.search(r'([\d.,]+)', price_text)
                    if match:
                        price_str = match.group(1)
                        price_str = price_str.replace(',', '.')
                        price = float(price_str)
                except Exception as e:
                    print(f"DEBUG: Price parsing error: {e} for text: {price_text}")
        
            product_data = {
                'title': title,
                'price': price,
                'url': product_url,
                'currency': self.website_currency,
                'source': self.website_that_is_scraped,  
                'source_currency': self.website_currency,
                'page': self.current_page
            }

            print(f"DEBUG: Extracted PcTech.bg product: {title} - {price}")

            tech_table = await page.query_selector('table.product_specification')
            if tech_table:
                list_items = await tech_table.query_selector_all('tr')
                for item in list_items:
                    try:
                        label_element = await item.query_selector('td.product_specification_title span')
                        value_element = await item.query_selector('td.product_specification_value')
                        
                        if label_element and value_element:
                            label = await label_element.inner_text()
                            value = await value_element.inner_text()
                            product_data[label.strip()] = value.strip()
                            print(f"DEBUG: Added property - {label.strip()}: {value.strip()}")
                    except Exception as e:
                        print(f"DEBUG: Skipping invalid property: {str(e)}")
                        continue

            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing PcTech.bg product page: {e}")
            return None