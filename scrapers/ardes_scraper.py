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

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)
        return f"https://www.ardes.bg/products?q={encoded_term}"

    def _construct_page_url(self, base_url, search_term, page):
        """Construct paginated URL properly for Ardes"""
        if page == 1:
            return base_url
        
        parsed_url = urlparse(base_url)
        query_params = parse_qs(parsed_url.query)
        
        query_params['page'] = [str(page)]
        
        new_query = urlencode(query_params, doseq=True)
        new_url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment
        ))
        
        return new_url

    async def _extract_product_links(self, page: Page, page_url: str) -> List[str]:
        """Get all product links using Playwright"""
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            await page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
            print(f"DEBUG: Page loaded: {page_url}")

            try:
                await page.wait_for_selector('div.products-grid, .search-results, .product-item', timeout=15000)
            except Exception as e:
                print(f"DEBUG: Could not find main product grid: {e}")
                screenshot_path = f"debug_ardes_{hash(page_url)}.png"
                await page.screenshot(path=screenshot_path, full_page=True)
                print(f"DEBUG: Screenshot saved to {screenshot_path}")
                return []

            selectors_to_try = [
                'div.products-grid div.prod-col',
                'div.prod-col',
                '.product-item',
                '.product-card',
                '.search-result-item'
            ]
            
            product_elements = []
            for selector in selectors_to_try:
                elements = await page.query_selector_all(selector)
                if elements:
                    product_elements = elements
                    print(f"DEBUG: Found {len(product_elements)} product elements with selector: {selector}")
                    break
            
            if not product_elements:
                print(f"DEBUG: No product elements found on page")
                page_content = await page.content()
                print(f"DEBUG: Page content (first 1000 chars): {page_content[:1000]}")
                return []

            for i, product in enumerate(product_elements):
                if hasattr(self, '_stop_requested') and self._stop_requested:
                    break

                print(f"DEBUG: Processing product {i+1}/{len(product_elements)}")
                
                await asyncio.sleep(0.05)
            
                link_selectors = [
                    'a[href^="/product/"]',
                    'a[href*="/product/"]',
                    'a.prod-link',
                    'a.title-link',
                    'a[itemprop="url"]',
                    'a'
                ]
            
                link_element = None
                href = None
                for selector in link_selectors:
                    try:
                        link_element = await product.query_selector(selector)
                        if link_element:
                            href = await link_element.get_attribute('href')
                            if href and '/product/' in href:
                                print(f"DEBUG: Found link with selector '{selector}': {href}")
                                break
                    except Exception as e:
                        print(f"DEBUG: Error with selector {selector}: {e}")
                        continue
                    link_element = None

                if href:
                    full_url = urljoin(self.base_domain, href)
                    clean_url = full_url.split('?')[0]
                
                    if '/product/' in clean_url and clean_url not in product_links:
                        title = "No Title"
                        title_selectors = [
                            '.prod-title',
                            '.title',
                            '.product-title',
                            'h3',
                            'h4',
                            '[itemprop="name"]'
                        ]
                        
                        for title_selector in title_selectors:
                            try:
                                title_element = await product.query_selector(title_selector)
                                if title_element:
                                    title_text = await title_element.inner_text()
                                    if title_text:
                                        title = title_text.strip()
                                        break
                            except:
                                continue

                        temp_product_data = {'title': title, 'description': ''}
                        
                        if self._should_filter_by_keywords(temp_product_data):
                            print(f'DEBUG: Skipped product based on exclusion keywords: {title}')
                            continue
                        
                        product_links.append(clean_url)
                        print(f"DEBUG: Added Ardes product: {title} - {clean_url}")
                    else:
                        print(f"DEBUG: Skipping URL (not a product or duplicate): {clean_url}")
                else:
                    print(f"DEBUG: Product {i+1} - No valid href found")
                    try:
                        product_html = await product.inner_text()
                        print(f"DEBUG: Product text: {product_html[:200]}...")
                    except:
                        pass

            print(f"DEBUG: Total Ardes product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from Ardes: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def _extract_product_data(self, page: Page, product_url: str) -> Optional[Dict[str, Any]]:
        """Extract detailed information using Playwright"""
        print(f"DEBUG: Parsing Ardes product: {product_url}")
        
        try:
            await page.goto(product_url, wait_until='domcontentloaded', timeout=30000)

            try:
                await page.wait_for_selector('div.product-title, h1.product-title, h1[itemprop="name"]', timeout=15000)
            except Exception as e:
                print(f"DEBUG: Could not find product title: {e}")
                await page.wait_for_selector('h1, .title, [itemprop="name"]', timeout=5000)

            title = "No Title"
            title_selectors = [
                'div.product-title h1',
                'h1.product-title',
                'h1[itemprop="name"]',
                'h1'
            ]
            
            for selector in title_selectors:
                title_element = await page.query_selector(selector)
                if title_element:
                    title_text = await title_element.inner_text()
                    if title_text:
                        title = title_text.strip()
                        break
            
            price = 0.0
            price_selectors = [
                'span.bgn-price',
                '.price-tag',
                '.product-price',
                '.price',
                '[itemprop="price"]',
                '.current-price'
            ]
            
            for selector in price_selectors:
                price_element = await page.query_selector(selector)
                if price_element:
                    try:
                        price_text = await price_element.inner_text()
                        price_text = price_text.strip()
                        
                        price_text = re.sub(r'[^\d.,]', '', price_text)
                        price_text = price_text.replace(',', '.')
                        
                        match = re.search(r'\d+\.?\d*', price_text)
                        if match:
                            price = float(match.group())
                            print(f"DEBUG: Found price with selector '{selector}': {price}")
                            break
                    except Exception as e:
                        print(f"DEBUG: Error parsing price with selector '{selector}': {e}")
                        continue
            
            if price == 0.0:
                print(f"DEBUG: Could not find price for product: {title}")
        
            product_data = {
                'title': title,
                'price': price,
                'url': product_url,
                'currency': self.website_currency,
                'source': 'Ardes'
            }

            print(f"DEBUG: Extracted Ardes product: {title} - {price} {self.website_currency}")

            try:
                table_selectors = [
                    'table.table',
                    'table.specifications',
                    'table.tech-spec',
                    'table[class*="spec"]',
                    'table'
                ]
                
                tech_table = None
                for selector in table_selectors:
                    tech_table = await page.query_selector(selector)
                    if tech_table:
                        break
                
                if tech_table:
                    list_items = await tech_table.query_selector_all('tr')
                    for list_item in list_items:
                        try:
                            label_element = await list_item.query_selector('th.clmn-head, th, td.label')
                            value_elements = await list_item.query_selector_all('td')

                            if label_element and len(value_elements) >= 1:
                                label = await label_element.inner_text()
                                value_element = value_elements[1] if len(value_elements) > 1 else value_elements[0]
                                value = await value_element.inner_text()
                                
                                label = label.strip() if label else ""
                                value = value.strip() if value else ""

                                if label and value:
                                    clean_label = re.sub(r'[:：\s]+$', '', label)
                                    product_data[clean_label] = value
                                    print(f"DEBUG: Added property: {clean_label} = {value}")
                        
                        except Exception as e:
                            print(f"DEBUG: Skipping table row: {str(e)}")
                            continue
            except Exception as e:
                print(f"DEBUG: Error extracting technical specs: {e}")

            print(f"DEBUG: Successfully parsed Ardes product: {title}")
            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing Ardes product page: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def _get_total_pages(self, page: Page, base_url: str) -> int:
        """Get total number of pages for pagination"""
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