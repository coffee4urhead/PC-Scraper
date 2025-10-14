import re
from urllib.parse import urljoin, quote
from base_scraper import PlaywrightBaseScraper

class AmazonScraper(PlaywrightBaseScraper):
    def __init__(self, gui_callback=None):
        super().__init__(gui_callback)

        self.gpu_keywords = [
            'graphics card', 'gpu', 'video card',
            'rtx', 'gtx', 'radeon', 'geforce',
            'pcie', 'pci-express', 'desktop'
        ]
        self.exclude_keywords = [
            'laptop', 'notebook', 'pc', 'computer', 'system',
            'prebuilt', 'desktop', 'all-in-one', 'mini pc'
        ]

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)

        return (
            f"https://www.amazon.com/s?k={encoded_term}"
            f"&crid={self.generate_random_crid()}"
            "&ref=nb_sb_noss_1"
        )

    def _construct_page_url(self, base_url, search_term, page):
        if page > 1:
            return f"{base_url}&page={page}"
        return base_url

    def _extract_product_links(self, page, page_url):
        """Get all product links from Amazon search results using Playwright"""
        product_links = []
        print(f"DEBUG: Extracting product links from Amazon: {page_url}")

        try:
            page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
            
            page.wait_for_selector('div[data-component-type="s-search-result"]', timeout=15000)
            
            product_elements = page.query_selector_all('div[data-component-type="s-search-result"]')
            print(f"DEBUG: Found {len(product_elements)} Amazon product elements")
            
            for product in product_elements:
                if self.stop_event.is_set():
                    break

                sponsored = product.query_selector('span:has-text("Sponsored")')
                if sponsored:
                    continue

                link_element = product.query_selector('a.a-link-normal.s-no-outline[href]')
                if link_element:
                    href = link_element.get_attribute('href')
                    if href:
                        full_url = urljoin('https://www.amazon.com', href)
                        clean_url = full_url.split('ref=')[0].split('?')[0]
                        if '/dp/' in clean_url and clean_url not in product_links:
                            product_links.append(clean_url)
                            
                            title_element = product.query_selector('h2 a span')
                            title = title_element.inner_text().strip() if title_element else "Unknown"
                            print(f"DEBUG: Added Amazon product: {title}")

            print(f"DEBUG: Total Amazon product links found: {len(product_links)}")
            return product_links

        except Exception as e:
            print(f"DEBUG: Error extracting product links from Amazon: {e}")
            try:
                page.screenshot(path="amazon_search_error.png")
            except:
                pass
            return []

    def _parse_product_page(self, page, product_url):
        """Extract detailed information from Amazon product page using Playwright"""
        print(f"DEBUG: Parsing Amazon product: {product_url}")
        
        try:
            page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
            
            page.wait_for_selector('span#productTitle', timeout=15000)
            
            title_element = page.query_selector('span#productTitle')
            title = title_element.inner_text().strip() if title_element else "No Title"
            
            price = "N/A"
            
            price_whole = page.query_selector('span.a-price-whole')
            price_fraction = page.query_selector('span.a-price-fraction')
            
            if price_whole and price_fraction:
                price_whole_text = price_whole.inner_text().strip()
                price_fraction_text = price_fraction.inner_text().strip()
                price = f"${price_whole_text}{price_fraction_text}"
            else:
                price_element = page.query_selector('span.a-price .a-offscreen')
                if price_element:
                    price = price_element.inner_text().strip()
            
            product_data = {
                'title': title,
                'price': price,
                'url': product_url
            }

            print(f"DEBUG: Extracted Amazon product: {title} - {price}")

            tech_table = page.query_selector('table.a-normal.a-spacing-micro')
            if not tech_table:
                tech_table = page.query_selector('table.prodDetTable')
                if not tech_table:
                    tech_table = page.query_selector('div#productDetails_db_sections')
            
            if tech_table:
                rows = tech_table.query_selector_all('tr')
                for row in rows:
                    try:
                        cells = row.query_selector_all('td')
                        if len(cells) >= 2:
                            label = cells[0].inner_text().strip().lower()
                            value = cells[1].inner_text().strip()
                            product_data[label] = value
                            print(f"DEBUG: Added Amazon spec: {label} = {value}")
                    except Exception as e:
                        print(f"DEBUG: Skipping invalid Amazon property: {str(e)}")
                        continue

            feature_bullets = page.query_selector('div#feature-bullets')
            if feature_bullets:
                bullets = feature_bullets.query_selector_all('li span.a-list-item')
                for i, bullet in enumerate(bullets):
                    product_data[f'feature_{i+1}'] = bullet.inner_text().strip()

            return product_data

        except Exception as e:
            print(f"DEBUG: Error parsing Amazon product page: {e}")
            try:
                page.screenshot(path="amazon_product_error.png")
            except:
                pass
            return None