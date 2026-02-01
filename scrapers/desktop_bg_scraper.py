import re
import asyncio
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from urllib.parse import quote, urljoin
from playwright.async_api import Page
from typing import List, Dict, Any, Optional
from .base_scraper import AsyncPlaywrightBaseScraper

class DesktopScraper(AsyncPlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://desktop.bg/"
        self.exclude_keywords = [
            "Лаптоп", 'Настолен компютър', 'HP Victus', 'Acer Predator Helios'
        ]
        self.update_gui_callback = update_gui_callback
        self.current_page = 1
        self.website_that_is_scraped = "Desktop.bg"

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)
        return f"{self.base_url}search?q={encoded_term}"

    def _construct_page_url(self, base_url, search_term):
        """Construct paginated URL for Desktop.bg using current_page counter"""
        if self.current_page == 1:
            return base_url
        
        parsed_url = urlparse(base_url)
        query_params = parse_qs(parsed_url.query)
        
        query_params['page'] = [str(self.current_page)]
        
        if 'q' not in query_params:
            query_params['q'] = [quote(search_term)]
        
        new_query = urlencode(query_params, doseq=True)
        new_url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment
        ))
        
        self.current_page += 1
        return new_url

    async def _extract_product_links(self, page: Page, page_url: str) -> List[str]:
        """Get all product links from a specific search results page using Playwright"""
        product_links = []
        print(f"DEBUG: _extract_product_links called for: {page_url}")

        for _ in range(3): 
            try:
                print(f"DEBUG: Navigating to search page...")
                await page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
            
                print("DEBUG: Waiting for products list...")
                await page.wait_for_selector('ul.products', timeout=10000)
            
                product_elements = await page.query_selector_all('ul.products li[id^="product_"]')
                print(f"DEBUG: Found {len(product_elements)} product elements")

                for product in product_elements:
                    if self._stop_requested:
                        break

                link_element = await product.query_selector('a[href]')
                if link_element:
                    href = await link_element.get_attribute('href')
                    title = await link_element.get_attribute('title')

                    temp_product_data = {'title': title if title else '', 'description': ''}
                    
                    if self._should_filter_by_keywords(temp_product_data):
                        print(f'DEBUG: Skipped product (exclusion keywords): {title}')
                        continue

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
                import traceback
                traceback.print_exc()
                try:
                    await page.screenshot(path=f"debug_error_{page_url.split('/')[-1]}.png")
                except:
                    pass
                return []

    async def _extract_product_data(self, page: Page, product_url: str) -> Optional[Dict[str, Any]]:
        """Extract detailed information from a product page using Playwright"""
        print(f"DEBUG: _extract_product_data called for: {product_url}")
        
        for _ in range(3): 
            try:
                await page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
            
                await page.wait_for_selector('div#content', timeout=10000)
            
                title_element = await page.query_selector('div#content h1[itemprop="name"]')
                title = await title_element.inner_text() if title_element else "N/A"
                title = title.strip() if title else "N/A"
            
                price_element = await page.query_selector('span[itemprop="price"]')
                price_text = await price_element.inner_text() if price_element else "N/A"
            
                price = 0.0
                if price_text != "N/A":
                    try:
                        price_text = price_text.replace("лв", "").replace(" ", "").strip()
                        price_text = price_text.replace(",", ".")
                        price = float(price_text)
                    except (ValueError, AttributeError) as e:
                        print(f"DEBUG: Could not parse price: {price_text}, error: {e}")
                        price = 0.0
            
                product_data = {
                    'title': title,
                    'price': price,
                    'url': product_url,
                    'currency': self.website_currency,
                    'source': 'Desktop.bg'
                }

                print(f"DEBUG: Extracted product: {title} - {price} {self.website_currency}")

                tech_table = await page.query_selector('table.product-characteristics')
                if tech_table:
                    rows = await tech_table.query_selector_all('tr')
                
                    for row in rows:
                        try:
                            label_element = await row.query_selector('th[scope="row"]')
                            value_element = await row.query_selector('td')
                        
                            if label_element and value_element:
                                label = await label_element.inner_text()
                                label = label.strip().lower()
                            
                                if label == "описание":
                                    continue
                            
                                value = await value_element.inner_text()
                                value = value.strip().lower()

                                product_data[label] = value
                                print(f"DEBUG: Added spec: {label} = {value}")

                        except Exception as e:
                            print(f"DEBUG: Skipping invalid property: {str(e)}")
                            continue

                if not self._should_include_product(product_data):
                    print(f"DEBUG: Product filtered out: {title}")
                    return None

                return product_data

            except Exception as e:
                print(f"DEBUG: Product page error: {str(e)}")
                import traceback
                traceback.print_exc()
                return None