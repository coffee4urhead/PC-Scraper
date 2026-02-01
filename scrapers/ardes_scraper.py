import random
import re
from urllib.parse import urljoin, quote, urlparse, parse_qs, urlencode, urlunparse
from scrapers.base_scraper import AsyncPlaywrightBaseScraper
from playwright.async_api import Page
from typing import List, Dict, Any, Optional
import asyncio

class ArdesScraper(AsyncPlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_domain = "https://www.ardes.bg"
        self.update_gui_callback = update_gui_callback
        self.current_page = 1

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)
        return f"https://www.ardes.bg/products?q={encoded_term}"

    def _construct_page_url(self, base_url, search_term):
        """Construct paginated URL properly for Ardes"""
        if self.current_page == 1:
            return base_url
        
        parsed_url = urlparse(base_url)
        query_params = parse_qs(parsed_url.query)

        query_params['page'] = [str(self.current_page)]

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
        """Get all product links using Playwright with retry logic"""
        print(f"DEBUG: Extracting product links from: {page_url}")
        
        async def extract_links_operation(attempt: int) -> Optional[List[str]]:
            await self._navigate_with_retry(page, page_url, attempt)
            
            product_grid_selectors = [
                'div.products-grid',
                '.search-results',
                '.product-item',
                '[class*="product"]',
                '.product-list'
            ]
            
            found_selector = await self._wait_for_selector_with_fallback(page, product_grid_selectors)
            if not found_selector:
                if attempt < 2:  
                    return None  
                else:
                    screenshot_path = f"debug_ardes_links_{hash(page_url)}_{attempt}.png"
                    await page.screenshot(path=screenshot_path, full_page=True)
                    print(f"DEBUG: Screenshot saved to {screenshot_path}")
                    return [] 
            
            link_elements = await page.query_selector_all('div.product-head > a[href]')
            print(f"DEBUG: Found {len(link_elements)} link elements")
            
            product_links = []
            for link in link_elements:
                try:
                    href = await link.get_attribute('href')
                    if href:
                        full_url = urljoin(self.base_domain, href)
                        product_links.append(full_url)
                except Exception as e:
                    print(f"DEBUG: Error processing link: {e}")
                    continue
            
            print(f"DEBUG: Total Ardes product links found: {len(product_links)}")
            
            if product_links:
                unique_links = list(dict.fromkeys(product_links))
                if len(product_links) != len(unique_links):
                    print(f"DEBUG: Removed {len(product_links) - len(unique_links)} duplicate URLs")
                return unique_links
            else:
                return None 
        
        result = await self._retry_operation(
            extract_links_operation, 
            f"Extract links from {page_url}",
            max_retries=3,
            initial_delay=2
        )
        
        return result if result is not None else []
    
    async def _extract_title_and_price(self, page: Page) -> tuple[str, float]:
        """Extract title and price from product page"""
        title = ""
        price = 0.0
        
        title_selectors = [
            'div.product-title h1',
            'h1.product-title',
            'h1.title',
            '[itemprop="name"]',
            'h1'
        ]
        
        title_element = None
        for selector in title_selectors:
            title_element = await page.query_selector(selector)
            if title_element:
                title = await title_element.inner_text()
                title = title.strip()
                break
        
        price_selectors = [
            'span.bgn-price',
            '.price',
            '[itemprop="price"]',
            '.product-price'
        ]
        
        for selector in price_selectors:
            price_element = await page.query_selector(selector)
            if price_element:
                price_text = await price_element.inner_text()
                print(f"DEBUG: Raw price text: {price_text}")
                
                price_text = price_text.strip()
                price_text = re.sub(r'[^\d,.-]', '', price_text)
                price_text = price_text.replace(',', '.')
                
                try:
                    price = float(price_text)
                    print(f"DEBUG: Parsed price: {price}")
                    break
                except ValueError:
                    print(f"DEBUG: Could not parse price to float: {price_text}")
                    continue
        
        return title, price
    
    async def _extract_technical_specs(self, page: Page) -> Dict[str, str]:
        """Extract technical specifications from product page"""
        product_data = {}
        
        tech_specs_selectors = [
            'ul.tech-specs-list',
            '.product-specifications',
            '.tech-specs',
            '.specifications'
        ]
        
        for selector in tech_specs_selectors:
            tech_specs_list = await page.query_selector(selector)
            if tech_specs_list:
                list_items = await tech_specs_list.query_selector_all('li')
                for li in list_items:
                    try:
                        label_element = await li.query_selector('span')
                        value_text = (await li.inner_text()).strip()  
                        label = (await label_element.inner_text()).strip() if label_element else ''
                        value = value_text.replace(label, '').strip() if label else value_text
                        
                        if label and value:
                            product_data[label] = value
                            print(f"DEBUG: Added property from list: {label} = {value}")
                    except Exception as e:
                        print(f"DEBUG: Skipping tech specs list item: {str(e)}")
                        continue
                break
        
        return product_data
    
    async def _extract_product_data(self, page: Page, product_url: str) -> Optional[Dict[str, Any]]:
        """Extract detailed information using Playwright with retry logic"""
        if product_url in self._processed_urls:
            print(f"DEBUG: Skipping already processed URL: {product_url}")
            return None
        
        print(f"DEBUG: Parsing Ardes product: {product_url}")
        
        async def extract_product_operation(attempt: int) -> Optional[Dict[str, Any]]:
            await self._navigate_with_retry(page, product_url, attempt)
            
            await self._rate_limit()
            
            product_page_selectors = [
                'div.product-title',
                'h1.product-title',
                '[itemprop="name"]',
                'h1'
            ]
            
            found_selector = await self._wait_for_selector_with_fallback(page, product_page_selectors, timeout=15000)
            if not found_selector:
                return None 
            
            title, price = await self._extract_title_and_price(page)
            tech_specs = await self._extract_technical_specs(page)
            
            if not title:
                print(f"DEBUG: Could not extract title for {product_url}")
                return None
            
            if price == 0.0:
                print(f"DEBUG: Could not find valid price for product: {title}")

            product_data = {
                'title': title,
                'price': price,
                'url': product_url,
                'currency': self.website_currency,
                'source': 'Ardes.bg',
                'page': self.current_page
            }
            
            if tech_specs:
                product_data.update(tech_specs)
            
            print(f"DEBUG: Extracted Ardes product: {title} - {price} {self.website_currency}")
            
            self._processed_urls.add(product_url)
            
            return product_data
        
        result = await self._retry_operation(
            extract_product_operation,
            f"Extract data from {product_url}",
            max_retries=3,
            initial_delay=2
        )
        
        if result is None:
            print(f"DEBUG: Failed to extract data from {product_url} after all retries")
        
        return result
    
    async def _get_total_pages(self, page: Page, base_url: str) -> int:
        """Get total number of pages for pagination"""
        async def get_pages_operation(attempt: int) -> Optional[int]:
            await self._navigate_with_retry(page, base_url, attempt)
            
            pagination_selectors = [
                '.pagination',
                '.pages',
                '.page-numbers',
                'ul.pagination'
            ]
            
            for selector in pagination_selectors:
                pagination = await page.query_selector(selector)
                if pagination:
                    page_links = await pagination.query_selector_all('a, li')
                    page_numbers = []
                    
                    for link in page_links:
                        try:
                            text = await link.inner_text()
                            if text.isdigit():
                                page_numbers.append(int(text))
                        except:
                            continue
                    
                    if page_numbers:
                        return max(page_numbers)
            
            return 1  
        
        result = await self._retry_operation(
            get_pages_operation,
            f"Get total pages from {base_url}",
            max_retries=2,  
            initial_delay=1
        )
        
        return result if result is not None else 1