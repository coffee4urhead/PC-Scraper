from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
import time
import random
import threading
import queue
import string

class BaseScraper(ABC):
    def __init__(self, gui_callback=None, driver=None):
        self.gui_callback = gui_callback
        self.scraping_thread = None
        self.stop_event = threading.Event()
        self.progress_queue = queue.Queue()
        self.results_queue = queue.Queue()
        self.delay_between_requests = 2
        self.max_pages = 10
        self.current_progress = 0
        self.driver = driver

    def _get_headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }

    def _get_html(self, url):
        try:
            if self.driver:  
                self.driver.get(url)
                time.sleep(2)  
                return self.driver.page_source
            else:  
                response = requests.get(url, headers=self._get_headers())
                response.raise_for_status()
                response.encoding = response.apparent_encoding
                print(response.headers)
                return response.text
        except Exception as e:
            self._update_gui({'type': 'error', 'message': f"Page fetch error: {str(e)}"})
            return None

    def generate_random_crid(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

    @abstractmethod
    def _get_base_url(self, search_term):
        """Website-specific search URL construction"""
        pass

    @abstractmethod
    def _parse_product_page(self, soup, product_url):
        """Website-specific product page parsing"""
        pass

    def _get_product_links(self, page_url):
        try:
            time.sleep(random.uniform(1, 2))
            html = self._get_html(page_url)

            if not html:
                return []

            soup = BeautifulSoup(html, 'html.parser')
            return self._extract_product_links(soup)

        except Exception as e:
            self._update_gui({'type': 'error', 'message': str(e)})
            return []

    @abstractmethod
    def _extract_product_links(self, soup):
        """Website-specific product link extraction"""
        pass

    def _get_product_details(self, product_url):
        try:
            html = self._get_html(product_url)
            if not html:
                return None

            soup = BeautifulSoup(html, 'html.parser')
            return self._parse_product_page(soup, product_url)

        except Exception as e:
            self._update_gui({'type': 'error', 'message': f"Product page error: {str(e)}"})
            return None

    def _update_gui(self, data):
        if self.gui_callback:
            self.gui_callback(data)

    def _update_progress(self, current, total):
        progress = int((current / total) * 100)
        if progress > self.current_progress:
            self.current_progress = progress
            self._update_gui({'type': 'progress', 'value': progress})

    def start_scraping(self, search_term, max_pages=3):
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
        self.stop_event.set()
        if self.scraping_thread:
            self.scraping_thread.join(timeout=1.0)
        if self.driver:
            self.driver.quit()  

    def _scrape_products(self, search_term, max_pages):
        try:
            base_url = self._get_base_url(search_term)
            total_pages = min(max_pages, self.max_pages)

            for page in range(1, total_pages + 1):
                if self.stop_event.is_set():
                    break

                self._update_progress(page - 1, total_pages)

                page_url = self._construct_page_url(base_url, search_term, page)

                product_links = self._get_product_links(page_url)
                if not product_links:
                    break

                for i, product_url in enumerate(product_links):
                    if self.stop_event.is_set():
                        break

                    self._update_progress(
                        (page - 1) + (i / len(product_links)),
                        total_pages
                    )

                    product = self._get_product_details(product_url)
                    if product:
                        self._update_gui({"type": "product", 'data': product})

                    time.sleep(self.delay_between_requests * random.uniform(1, 2))

            self._update_progress(total_pages, total_pages)
            self._update_gui({'type': 'complete'})

        except Exception as e:
            self._update_gui({'type': 'error', 'message': str(e)})
        finally:
            self.stop_event.set()

    @abstractmethod
    def _construct_page_url(self, base_url, search_term, page):
        """Construct the URL for a specific page number"""
        pass