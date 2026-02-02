import re
from urllib.parse import quote, urljoin, urlparse, parse_qs, urlencode, urlunparse
from .base_scraper import AsyncPlaywrightBaseScraper

class AmazonComScraper(AsyncPlaywrightBaseScraper):
    def __init__(self, website_currency, update_gui_callback=None):
        super().__init__(website_currency, update_gui_callback)
        self.base_url = "https://www.amazon.com/"
        self.update_gui_callback = update_gui_callback
        self.current_page = 1
        self.website_that_is_scraped = "Amazon.com"

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)
        return f"{self.base_url}s?k={encoded_term}&crid=2J0PCSZU19ONB&sprefix={encoded_term}%2Caps%2C153&ref=nb_sb_noss_2"

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

    async def _extract_product_links(self, page, page_url):
        """Get all product links using Playwright"""
        product_links = []
        print(f"DEBUG: Extracting product links from: {page_url}")

        try:
            await page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
        
            await page.wait_for_selector('div[data-component-type="s-search-result"]', timeout=10000)

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
                    title_text = await title_element.inner_text()
                    title = title_text.strip()
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
                            print(f"DEBUG: Added Amazon.com product: {title}")
                    else:
                        print(f"DEBUG: Product {i+1} - Not a product link: {href}")
                else:
                    print(f"DEBUG: Product {i+1} - No link element found")

            print(f"DEBUG: Total Amazon.com product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from Amazon.com: {e}")
            return []

    async def _extract_product_data(self, page, product_url):
        """Extract detailed information using Playwright"""
        print(f"DEBUG: Parsing Amazon.com product: {product_url}")

        try:
            await page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
    
            await page.wait_for_selector('h1#title span#productTitle', timeout=10000)

            title_element = await page.query_selector('h1#title span#productTitle')
            title_text = await title_element.inner_text() if title_element else "N/A"
            title = title_text.strip()
    
            # FIXED: Price extraction
            price_element_whole = await page.query_selector('span.a-price-whole')
            price_element_fraction = await page.query_selector('span.a-price-fraction')
        
            if price_element_whole and price_element_fraction:
                whole_text = await price_element_whole.inner_text()
                fraction_text = await price_element_fraction.inner_text()

                whole_part = whole_text.strip().replace('.', '').replace('\n', '').replace(' ', '')
                fraction_part = fraction_text.strip().replace('\n', '').replace(' ', '')
            
                print(f"DEBUG: Raw whole: '{whole_text}', Cleaned: '{whole_part}'")
                print(f"DEBUG: Raw fraction: '{fraction_text}', Cleaned: '{fraction_part}'")
                
                if whole_part.isdigit() and fraction_part.isdigit():
                    price_text = f"${whole_part}.{fraction_part}"
                else:
                    print(f"DEBUG: Invalid price parts: whole='{whole_part}', fraction='{fraction_part}'")
                    price_text = "N/A"
            else:
                price_text = "N/A"
    
            product_data = {
                'title': title,
                'price': price_text,
                'url': product_url,
                'currency': self.website_currency,
                'source': 'Amazon.com',
                'source_currency': self.website_currency,
                'page': self.current_page
            }

            print(f"DEBUG: Extracted Amazon.com product: {title} - {price_text}")

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
                            label = label_text.strip().lower()
                            value_text = await value_element.inner_text()
                            value = value_text.strip().lower()

                            if value:
                                product_data[label] = value
                                print(f"DEBUG: Added Amazon.com spec: {label} = {value}")
                        else:
                            print(f"DEBUG: Skipping table row with insufficient cells: {len(td_elements)}")
                    
                    except Exception as e:
                        print(f"DEBUG: Skipping invalid property: {str(e)}")
                        continue

            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing Amazon.com product page: {e}")
            return None