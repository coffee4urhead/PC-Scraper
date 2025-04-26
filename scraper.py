import re
from urllib.parse import urljoin, quote
import requests
import time
import threading
import queue
from bs4 import BeautifulSoup
import random
import string


class AmazonGPUScraper:
    def __init__(self, gui_callback=None):
        self.gui_callback = gui_callback
        self.scraping_thread = None
        self.stop_event = threading.Event()
        self.progress_queue = queue.Queue()
        self.results_queue = queue.Queue()

        # Configuration
        self.delay_between_requests = 2  # seconds
        self.max_pages = 3
        self.current_progress = 0

        # GPU identification parameters
        self.gpu_keywords = [
            'graphics card', 'gpu', 'video card',
            'rtx', 'gtx', 'radeon', 'geforce',
            'pcie', 'pci-express', 'desktop'
        ]
        self.exclude_keywords = [
            'laptop', 'notebook', 'pc', 'computer', 'system',
            'prebuilt', 'desktop', 'all-in-one', 'mini pc'
        ]

    def _get_headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
            "TE": "trailers"
        }

    def generate_random_crid(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)

        return (
            f"https://www.amazon.com/s?k={encoded_term}"
            f"&crid={self.generate_random_crid()}"
            "&ref=nb_sb_noss_1"
        )

    def _get_product_links(self, page_url):
        """Get all product links from a specific search results page URL"""
        product_links = []
        try:
            time.sleep(1 + random.random())
            response = requests.get(page_url, headers=self._get_headers())
            response.raise_for_status()

            if "captcha" in response.text.lower():
                self._update_gui({'type': 'error', 'message': "CAPTCHA detected"})
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            products = soup.find_all('div', {'data-component-type': 's-search-result'})

            for product in products:
                if self.stop_event.is_set():
                    break

                # Skip sponsored ads
                if product.find('span', string=re.compile('Sponsored')):
                    continue

                link_tag = product.find('a', {'class': 'a-link-normal s-no-outline'})
                if link_tag and 'href' in link_tag.attrs:
                    full_url = urljoin('https://www.amazon.com', link_tag['href'])
                    clean_url = full_url.split('ref=')[0].split('?')[0]
                    if '/dp/' in clean_url:
                        product_links.append(clean_url)

            return product_links

        except Exception as e:
            self._update_gui({'type': 'error', 'message': str(e)})
            return []

    def _get_product_details(self, product_url):
        """Extract detailed information from a product page"""
        try:
            response = requests.get(product_url, headers=self._get_headers())
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract product title
            title = soup.find('span', {'id': 'productTitle'})
            title = title.get_text(strip=True) if title else "No Title"

            # Extract price
            price_whole = soup.find('span', {'class': 'a-price-whole'})
            price_fraction = soup.find('span', {'class': 'a-price-fraction'})
            price = f"${price_whole.get_text(strip=True)}.{price_fraction.get_text(strip=True)}" if price_whole and price_fraction else "N/A"

            # Extract technical details
            tech_details = {}
            tech_table = soup.find('table', {'id': 'productDetails_techSpec_section_1'})
            if tech_table:
                for row in tech_table.find_all('tr'):
                    th = row.find('th')
                    td = row.find('td')
                    if th and td:
                        tech_details[th.get_text(strip=True)] = td.get_text(strip=True)

            return {
                'title': title,
                'price': price,
                'url': product_url,
                'technical_details': tech_details,
            }

        except Exception as e:
            self._update_gui({'type': 'error', 'message': f"Product page error: {str(e)}"})
            return None

    def _update_gui(self, data):
        """Thread-safe GUI update method"""
        if self.gui_callback:
            self.gui_callback(data)

    def _update_progress(self, current, total):
        """Calculate and send progress updates"""
        progress = int((current / total) * 100)
        if progress > self.current_progress:  # Only send if progress increased
            self.current_progress = progress
            self._update_gui({'type': 'progress', 'value': progress})

    def start_scraping(self, search_term, max_pages=3):
        """Start the scraping process in a background thread"""
        if self.scraping_thread and self.scraping_thread.is_alive():
            self._update_gui({'type': 'error', 'message': "Scraper already running"})
            return False

        self.stop_event.clear()
        self.current_progress = 0
        self.scraping_thread = threading.Thread(
            target=self._scrape_products,
            args=(search_term, max_pages),
            daemon=True
        )
        self.scraping_thread.start()
        return True

    def stop_scraping(self):
        """Stop the ongoing scraping process"""
        self.stop_event.set()
        if self.scraping_thread:
            self.scraping_thread.join(timeout=1.0)

    def _scrape_products(self, search_term, max_pages):
        """Main scraping logic running in background thread"""
        try:
            base_url = self._get_base_url(search_term)
            total_pages = min(max_pages, 5)  # Don't scrape more than 5 pages

            for page in range(1, total_pages + 1):
                if self.stop_event.is_set():
                    break

                # Update page-level progress
                self._update_progress(page - 1, total_pages)

                page_url = f"{base_url}&page={page}"
                product_links = self._get_product_links(page_url)

                if not product_links:
                    break

                # Process each product on the page
                for i, product_url in enumerate(product_links):
                    if self.stop_event.is_set():
                        break

                    # Update item-level progress within page
                    self._update_progress(
                        (page - 1) + (i / len(product_links)),
                        total_pages
                    )

                    product = self._get_product_details(product_url)
                    if product:
                        # Verify it's a physical GPU
                        title = product['title'].lower()
                        is_gpu = any(kw in title for kw in self.gpu_keywords)
                        is_not_gpu = any(kw in title for kw in self.exclude_keywords)

                        if is_gpu and not is_not_gpu:
                            self._update_gui({
                                'type': 'product',
                                'data': product,
                                'page': page
                            })

                    time.sleep(self.delay_between_requests * random.uniform(0.5, 1.5))

                time.sleep(self.delay_between_requests * 2)

            # Final progress update
            self._update_progress(total_pages, total_pages)
            self._update_gui({'type': 'complete'})

        except Exception as e:
            self._update_gui({'type': 'error', 'message': str(e)})
        finally:
            self.stop_event.set()