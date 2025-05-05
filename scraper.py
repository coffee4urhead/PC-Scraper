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
        self.cl_search_term = ""

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
        self.cl_search_term = search_term
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
            time.sleep(random.uniform(2, 5))
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
                    if '/dp/' in clean_url and clean_url not in product_links:
                        product_links.append(clean_url)

            return product_links

        except Exception as e:
            self._update_gui({'type': 'error', 'message': str(e)})
            return []

    def _get_product_details(self, product_url):
        """Extract detailed information from a product page and structure it for Excel output"""
        try:
            response = requests.get(product_url, headers=self._get_headers())
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            title = soup.find('span', {'id': 'productTitle'})
            title = title.get_text(strip=True) if title else "No Title"

            price_whole = soup.find('span', {'class': 'a-price-whole'})
            price_fraction = soup.find('span', {'class': 'a-price-fraction'})
            price = f"${price_whole.get_text(strip=True)}.{price_fraction.get_text(strip=True)}" if price_whole and price_fraction else "N/A"

            product_data = {
                'title': title,
                'price': price,
                'url': product_url,
                'brand': "N/A",
                'gpu_model': "N/A",
                'graphics_coprocessor': "N/A",
                'graphics_ram_size': "N/A",
                'gpu_clock_speed': "N/A",
                'video_output_resolution': "N/A"
            }

            tech_table = soup.find('table', {'class': 'a-normal a-spacing-micro'})
            if tech_table:
                for row in tech_table.find_all('tr'):
                    tds = row.find_all('td')
                    if len(tds) >= 2:
                        label = tds[0].get_text(strip=True).lower()
                        value = tds[1].get_text(strip=True)

                        if 'brand' in label:
                            product_data['brand'] = value
                        elif 'model' in label:
                            product_data['gpu_model'] = value
                        elif 'coprocessor' in label or 'graphics processor' in label:
                            product_data['graphics_coprocessor'] = value
                        elif 'memory size' in label or 'ram size' in label or 'vram' in label:
                            product_data['graphics_ram_size'] = value
                        elif 'clock speed' in label or 'gpu speed' in label:
                            product_data['gpu_clock_speed'] = value
                        elif 'output' in label or 'interface' in label or 'resolution' in label:
                            product_data['video_output_resolution'] = value

            if product_data['brand'] == "N/A":
                if 'nvidia' in title.lower():
                    product_data['brand'] = "NVIDIA"
                elif 'amd' in title.lower() or 'radeon' in title.lower():
                    product_data['brand'] = "AMD"
                elif 'asus' in title.lower():
                    product_data['brand'] = "ASUS"
                elif 'msi' in title.lower():
                    product_data['brand'] = "MSI"

            if product_data['gpu_model'] == "N/A":
                model_match = re.search(r'(RTX \d{4}|RX \d{4}|GTX \d{4}|Radeon \w+)', title, re.IGNORECASE)
                if model_match:
                    product_data['gpu_model'] = model_match.group(0).upper()

            return product_data

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

                    time.sleep(self.delay_between_requests * random.uniform(2, 5))

                time.sleep(self.delay_between_requests * 2)

            # Final progress update
            self._update_progress(total_pages, total_pages)
            self._update_gui({'type': 'complete'})

        except Exception as e:
            self._update_gui({'type': 'error', 'message': str(e)})
        finally:
            self.stop_event.set()