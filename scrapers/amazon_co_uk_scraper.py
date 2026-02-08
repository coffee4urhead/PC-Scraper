import re
import random
from urllib.parse import quote, urljoin
from .base_scraper import AsyncPlaywrightBaseScraper

class AmazonCoUkScraper(AsyncPlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://www.amazon.co.uk/"
        self.website_that_is_scraped = "Amazon.co.uk"
        self.current_page = 1
        self.update_gui_callback = update_gui_callback

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)
        return f"{self.base_url}s?k={encoded_term}"

    def _construct_page_url(self, base_url, search_term):
        if self.current_page >= 1:
            return f"{self.base_url}s?k={quote(search_term)}&page={self.current_page}"
        return base_url

    async def _extract_product_links(self, page, page_url):
        """Get all product links using Playwright"""
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            await page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
        
            await page.wait_for_selector('div[data-component-type="s-search-result"]', timeout=15000)
            
            html = await page.content()
            if "We’re sorry" in html or "Robot Check" in html:
                print("DEBUG: Amazon.co.uk detected bot — retrying once...")
                await asyncio.sleep(self.delay_between_requests * random.uniform(1, self.random_delay_multiplier))
                await page.reload(wait_until="domcontentloaded")

            product_elements = await page.query_selector_all('div[data-component-type="s-search-result"]')
            print(f"DEBUG: Found {len(product_elements)} product elements")
        
            for i, product in enumerate(product_elements):
                if self._stop_event.is_set():
                    break

                print(f"DEBUG: Processing product {i+1}/{len(product_elements)}")
            
                sponsored = await product.query_selector('span:has-text("Sponsored")')
                if sponsored:
                    print(f"DEBUG: Product {i+1} - Skipping sponsored")
                    continue

                title_element = await product.query_selector('div[data-cy=title-recipe]')
                if title_element:
                    title = await title_element.inner_text()
                    title = title.strip()
                else:
                    print(f"DEBUG: Product {i+1} - No title found")
                    continue

                print(f"DEBUG: Product {i+1} - Title: '{title}'")
            
                temp_product_data = {'title': title, 'description': ''}
                if self._should_filter_by_keywords(temp_product_data):
                    print(f'Skipped product because it was in the exclusion keywords: {self.exclude_keywords}')
                    continue

                link_element = await product.query_selector('a.a-link-normal')
                if link_element:
                    href = await link_element.get_attribute('href')
                    if href and '/dp/' in href:  
                        full_url = urljoin(self.base_url, href)
                        clean_url = full_url.split('ref=')[0].split('?')[0]
                        if clean_url not in product_links:
                            product_links.append(clean_url)
                            print(f"DEBUG: Added Amazon.co.uk product: {title}")
                    else:
                        print(f"DEBUG: Product {i+1} - Not a product link: {href}")
                else:
                    print(f"DEBUG: Product {i+1} - No link element found")

            print(f"DEBUG: Total Amazon.co.uk product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from Amazon.co.uk: {e}")
            return []

    async def _extract_product_data(self, page, product_url):
        """Extract detailed information using Playwright"""
        print(f"DEBUG: Parsing Amazon.co.uk product: {product_url}")

        try:
            await page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
    
            await page.wait_for_selector('h1#title span#productTitle', timeout=10000)

            title_element = await page.query_selector('h1#title span#productTitle')
            title = ""
            if title_element:
                title_text = await title_element.inner_text()
                title = title_text.strip()
            else:
                title = "N/A"
    
            price_element_whole = await page.query_selector('span.a-price-whole')
            price_element_fraction = await page.query_selector('span.a-price-fraction')
        
            price = 0.0
            if price_element_whole and price_element_fraction:
                whole_text = await price_element_whole.inner_text()
                fraction_text = await price_element_fraction.inner_text()
                whole_part = whole_text.strip()
                fraction_part = fraction_text.strip()
                price_text = f"{whole_part}.{fraction_part}"
                
                if '.' in whole_part:
                    whole_part = whole_part.rstrip('.')
                
                price_text = f"{whole_part}.{fraction_part}"
                try:
                    clean_price = price_text.replace('£', '').replace('$', '').replace(',', '').strip()
                    price = float(clean_price)
                except ValueError:
                    print(f"DEBUG: Could not convert price: '{price_text}'")
                    price = 0.0
            else:
                price_selectors = [
                    'span.a-price[data-a-color="base"] span.a-offscreen',
                    'span[data-a-color="price"] span.a-offscreen',
                    '.a-price .a-offscreen',
                    '#price_inside_buybox',
                    '#priceblock_ourprice',
                    '#priceblock_dealprice'
                ]
                
                for selector in price_selectors:
                    alt_price_element = await page.query_selector(selector)
                    if alt_price_element:
                        alt_price_text = await alt_price_element.inner_text()
                        try:
                            clean_price = alt_price_text.replace('£', '').replace('$', '').replace(',', '').strip()
                            price = float(clean_price)
                            print(f"DEBUG: Found price with alternative selector '{selector}': {price}")
                            break
                        except ValueError:
                            continue
                else:
                    print(f"DEBUG: No price found for product: {title}")
    
            product_data = {
                'title': title,
                'price': price,
                'url': product_url,
                'currency': self.website_currency,
                'source': 'Amazon.co.uk',
                'source_currency': self.website_currency,  
                'page': self.current_page  
            }

            print(f"DEBUG: Extracted Amazon.co.uk product: {title} - £{price}")

            tech_table = await page.query_selector('table[role=list]')
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
                                print(f"DEBUG: Added Amazon.co.uk spec: {label} = {value}")
                        else:
                            print(f"DEBUG: Skipping table row with insufficient cells: {len(td_elements)}")
                    
                    except Exception as e:
                        print(f"DEBUG: Skipping invalid property: {str(e)}")
                        continue

            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing Amazon.co.uk product page: {e}")
            return None