import re
from urllib.parse import quote, urljoin
from .base_scraper import AsyncPlaywrightBaseScraper

class GtComputersScraper(AsyncPlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://gtcomputers.bg/"
        self.website_that_is_scraped = "GtComputers.bg"
        self.current_page = 1
        self.update_gui_callback = update_gui_callback

    def _get_base_url(self, search_term):
        encoded_term = quote(search_term)
        return f"{self.base_url}search_tags/?s={encoded_term}"

    def _construct_page_url(self, base_url, search_term):
        if self.current_page >= 1:
            return f"{self.base_url}search_tags/?s={quote(search_term)}&pg={self.current_page}"
        return base_url

    async def _extract_product_links(self, page, page_url):
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            await page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
            
            await page.wait_for_selector('div.pt-1', timeout=10000)

            product_elements = await page.query_selector_all('div.pt-1')
            print(f"DEBUG: Found {len(product_elements)} product elements")
            
            for product in product_elements:
                if self._stop_event.is_set():
                    break

                sponsored = await product.query_selector('span:has-text("Sponsored")')
                if sponsored:
                    continue

                title_element = await product.query_selector('a[href]')
                title = ""
                if title_element:
                    title_text = await title_element.inner_text()
                    title = title_text.strip()
                
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
                            print(f"DEBUG: Added GtComputers product: {title}")

            print(f"DEBUG: Total GtComputers product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from GtComputers: {e}")
            return []

    async def _extract_gt_computers_price(self, price_text):
        try:
            clean_price = re.sub(r'[^\d,.]', '', price_text)
            if ',' in clean_price and '.' in clean_price:
                clean_price = clean_price.replace('.', '').replace(',', '.')
            elif ',' in clean_price:
                clean_price = clean_price.replace(',', '.')
            clean_price = re.sub(r'[^\d.]', '', clean_price)
            if clean_price:
                return float(clean_price)
            return 0.0
        except ValueError:
            print(f"DEBUG: Could not convert price: '{price_text}'")
            return 0.0

    async def _extract_product_data(self, page, product_url):
        print(f"DEBUG: Parsing GtComputers product: {product_url}")
    
        try:
            await page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
            
            await page.wait_for_selector('div.sttop-mt1 h1.tit1', timeout=10000)

            title_element = await page.query_selector('div.sttop-mt1 h1.tit1')
            title = ""
            if title_element:
                title_text = await title_element.inner_text()
                title = title_text.strip()
            else:
                title = "N/A"
        
            price_element = await page.query_selector('div.pr_pr')
            price = 0.0
            if price_element:
                price_text = await price_element.inner_text()
                price_text = price_text.strip()
                bgn_part = price_text.split('/')[0].replace("Цена", "").strip()
            
                price = await self._extract_gt_computers_price(bgn_part)
        
            product_data = {
                'title': title,
                'price': price,
                'url': product_url,
                'currency': self.website_currency,
                'source': 'GtComputers.bg',
                'source_currency': self.website_currency,
                'page': self.current_page
            }

            print(f"DEBUG: Extracted GtComputers product: {title} - {price}")

            tech_table = await page.query_selector('table.table_filter')
            if tech_table:
                list_items = await tech_table.query_selector_all('tr')
                for item in list_items:
                    try:
                        td_elements = await item.query_selector_all('td')
                        if len(td_elements) >= 2:
                            label_element = td_elements[0]
                            value_element = td_elements[1]
                        
                            label_text = await label_element.inner_text()
                            value_text = await value_element.inner_text()
                            label = label_text.strip().lower()
                            value = value_text.strip().lower()
                        
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