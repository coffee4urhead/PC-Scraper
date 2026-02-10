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
        self.website_that_is_scraped = "Ardes.bg"

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)
        return f"https://www.ardes.bg/products?q={encoded_term}"

    def _construct_page_url(self, base_url, search_term):
        """Construct paginated URL properly for Ardes"""
        if self.current_page == 1:
            return base_url
    
        parsed_url = urlparse(base_url)
        path_parts = parsed_url.path.split('/')
    
        if 'page' in path_parts:
            for i, part in enumerate(path_parts):
                if part == 'page' and i + 1 < len(path_parts):
                    path_parts[i + 1] = str(self.current_page)
                    break
        else:
            if 'products' in path_parts:
                products_index = path_parts.index('products')
                path_parts.insert(products_index + 1, 'page')
                path_parts.insert(products_index + 2, str(self.current_page))
            else:
                if parsed_url.path.endswith('/'):
                    new_path = f"{parsed_url.path}page/{self.current_page}"
                else:
                    new_path = f"{parsed_url.path}/page/{self.current_page}"
                parsed_url = parsed_url._replace(path=new_path)
                self.current_page += 1
                return urlunparse(parsed_url)
    
        new_path = '/'.join(path_parts)
        parsed_url = parsed_url._replace(path=new_path)
    
        self.current_page += 1
        return urlunparse(parsed_url)
    
    async def _extract_product_links(self, page: Page, page_url: str) -> List[str]:
        """Get all product links using Playwright with retry logic"""
        print(f"DEBUG: Extracting product links from: {page_url}")

        for attempt in range(3):
            try:
                print(f"DEBUG: Attempt {attempt + 1} for {page_url}")

                await page.mouse.wheel(0, random.randint(400, 900))
                await asyncio.sleep(random.uniform(0.5, 1.5))
        
                wait_strategies = ['domcontentloaded', 'load', 'networkidle']
                wait_strategy = wait_strategies[min(attempt, len(wait_strategies)-1)]
        
                await page.goto(page_url, wait_until=wait_strategy, timeout=30000)
                print(f"DEBUG: Page loaded successfully: {page_url} (wait_until: {wait_strategy})")
            
                # Wait for product grid
                selectors_to_try = [
                    'div.products-grid',
                    '.search-results', 
                    '.product-item',
                    '[class*="product"]',
                    '.product-list'
                ]
        
                found_selector = None
                for selector in selectors_to_try:
                    try:
                        await page.wait_for_selector(selector, timeout=10000)
                        found_selector = selector
                        print(f"DEBUG: Found product grid with selector: {selector}")
                        break
                    except Exception:
                        continue
        
                if not found_selector:
                    print(f"DEBUG: Could not find main product grid on attempt {attempt + 1}")
                    if attempt < 2:
                        print(f"DEBUG: Retrying in {2 * (attempt + 1)} seconds...")
                        await asyncio.sleep(2 * (attempt + 1))  
                        continue
                    else:
                        screenshot_path = f"debug_ardes_{hash(page_url)}_{attempt}.png"
                        await page.screenshot(path=screenshot_path, full_page=True)
                        print(f"DEBUG: Screenshot saved to {screenshot_path}")
                        return []
        
                # Get ALL product elements
                product_elements = await page.query_selector_all('div.product')
                print(f"DEBUG: Found {len(product_elements)} product elements")
            
                # DEBUG: Let's see what selectors are available on the first product
                if product_elements:
                    first_product = product_elements[0]
                    # Try to get all text content to see what's available
                    all_text = await first_product.inner_text()
                    print(f"DEBUG: First product full text: {all_text}")
                
                    # Try different selectors to find the full title
                    test_selectors = [
                        'span.ellip-line',
                        '.product-title',
                        '.name',
                        'h2',
                        'h3',
                        'a',
                        'div.product-head',
                        'div.product-head a'
                    ]
                
                    for selector in test_selectors:
                        element = await first_product.query_selector(selector)
                        if element:
                            text = await element.inner_text()
                            print(f"DEBUG: Selector '{selector}' gives: {text.strip()[:100]}")
            
                product_links = []
                skipped_count = 0
            
                # Process each product element individually
                for product in product_elements:
                    try:
                        # Try multiple selectors to get the FULL title
                        title_text = ""
                        title_selectors = [
                            'div.product-head a',  # This might contain the full title
                            'span.ellip-line',
                            '.product-title',
                            '.name',
                            'h2',
                            'h3',
                            'a[href]'
                        ]
                    
                        for selector in title_selectors:
                            title_element = await product.query_selector(selector)
                            if title_element:
                                text = await title_element.inner_text()
                                if text and len(text.strip()) > 5:  # More than just "(2.9GHz)"
                                    title_text = text.strip()
                                    break
                    
                        # If we still have a short title, get the full link text
                        if not title_text or len(title_text) < 10:
                            link_element = await product.query_selector('a[href]')
                            if link_element:
                                title_text = await link_element.inner_text()
                                title_text = title_text.strip()
                    
                        print(f"DEBUG: Extracted title: {title_text}")
                    
                        # Check if product should be filtered by keywords
                        if title_text:
                            temp_product_data = {'title': title_text, 'description': ''}
                            if self._should_filter_by_keywords(temp_product_data):
                                print(f'Skipped product "{title_text}" because it matches exclusion keywords')
                                skipped_count += 1
                                continue  # Skip to next product
                    
                        # Get link
                        link_element = await product.query_selector('div.product-head > a[href]')
                        if not link_element:
                            link_element = await product.query_selector('a[href]')
                    
                        if link_element:
                            href = await link_element.get_attribute('href')
                            if href:
                                full_url = urljoin(self.base_domain, href)
                                product_links.append(full_url)
                                print(f"DEBUG: Added product link for: {title_text}")
                            
                    except Exception as e:
                        print(f"DEBUG: Error processing product: {e}")
                        continue
            
                print(f"DEBUG: Total Ardes product links found: {len(product_links)} (skipped {skipped_count} products)")
        
                if product_links:
                    unique_links = list(dict.fromkeys(product_links))
                    if len(product_links) != len(unique_links):
                        print(f"DEBUG: Removed {len(product_links) - len(unique_links)} duplicate URLs")
                    return unique_links
                else:
                    print(f"DEBUG: No product links found on attempt {attempt + 1}")
                    if attempt < 2:
                        print(f"DEBUG: Retrying in {2 * (attempt + 1)} seconds...")
                        await asyncio.sleep(2 * (attempt + 1))  
                        continue
        
            except Exception as e:
                print(f"DEBUG: Attempt {attempt + 1} failed for {page_url}: {e}")
        
                if attempt < 2: 
                    print(f"DEBUG: Retrying in {2 * (attempt + 1)} seconds...")
                    await asyncio.sleep(2 * (attempt + 1))  
                    continue  
                else:
                    print(f"DEBUG: All attempts failed for {page_url}")
                    import traceback
                    traceback.print_exc()
                    return []

        return []
    
    async def _extract_product_data(self, page: Page, product_url: str) -> Optional[Dict[str, Any]]:
        """Extract detailed information using Playwright"""
        print(f"DEBUG: Parsing Ardes product: {product_url}")
        
        for attempt in range(3): 
            try:
                await page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
                await self._rate_limit()
                try:
                    await page.wait_for_selector('div.product-title', timeout=15000)
                except Exception as e:
                    print(f"DEBUG: Could not find product title: {e}")
                    await page.wait_for_selector('h1, .title, [itemprop="name"]', timeout=5000)

                title_element = await page.query_selector('div.product-title h1')
                title = ""
                if title_element:
                    title = await title_element.inner_text()
                    title = title.strip()

                price = 0.0

                price_element = await page.query_selector('span.bgn-price')
                if price_element:
                    price = await price_element.inner_text()
                    print(f"DEBUG: Raw price text: {price}")

                    price_text = price.strip()
                    price_text = re.sub(r'[^\d,.-]', '', price_text)
                    price_text = price_text.replace(',', '.')

                    try:
                        price = float(price_text)
                        print(f"DEBUG: Parsed price: {price}")
                    except ValueError:
                        print(f"DEBUG: Could not parse price to float: {price_text}")
                        price = 0.0
                    else:
                        print("DEBUG: Price element not found")
                
                product_data = {}
                tech_specs_list = await page.query_selector('ul.tech-specs-list')
                if tech_specs_list:
                    list_items = await tech_specs_list.query_selector_all('li')
                    for li in list_items:
                        try:
                            if li:
                                label_element = await li.query_selector('span')
                                value_text = (await li.inner_text()).strip()  
                                label = (await label_element.inner_text()).strip() if label_element else ''
                                value = value_text.replace(label, '').strip() if label else value_text
                        
                                product_data[label] = value
                                print(f"DEBUG: Added property from list: {label} = {value}")
                        except Exception as e:
                            print(f"DEBUG: Skipping tech specs list item: {str(e)}")
                            continue

                if price == 0.0:
                    print(f"DEBUG: Could not find price for product: {title}")

                product_data.update({
                    'title': title,
                    'price': price,
                    'url': product_url,
                    'currency': self.website_currency,
                    'source': 'Ardes.bg',
                    'source_currency': self.website_currency,
                    'page': self.current_page
                })
                print(f"DEBUG: Extracted Ardes product: {title} - {price} {self.website_currency}")
                return product_data
            
            except Exception as e:
                    print(f"DEBUG: Attempt {attempt + 1} failed for {product_url}: {e}")
            
            if attempt < 2: 
                print(f"DEBUG: Retrying in {2 * (attempt + 1)} seconds...")
                await asyncio.sleep(2 * (attempt + 1))  
                continue  
            else:
                print(f"DEBUG: All attempts failed for {product_url}")
                import traceback
                traceback.print_exc()
                return []

    async def _get_total_pages(self, page: Page, base_url: str) -> int:
        """Get total number of pages for pagination"""
        await page.mouse.wheel(0, random.randint(400, 900))
        try:
            await page.goto(base_url, wait_until='domcontentloaded', timeout=30000)
            
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
            
        except Exception as e:
            print(f"DEBUG: Error getting total pages: {e}")
            return 1