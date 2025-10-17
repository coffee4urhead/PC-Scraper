from abc import ABC, abstractmethod
import time
import random
import re
import threading
import queue
import string
from playwright.sync_api import sync_playwright

class PlaywrightBaseScraper(ABC):
    def __init__(self, gui_callback=None, driver=None):
        self.currency_symbol = "лв"
        self.currency_code = "BGN"
        self.gui_callback = gui_callback
        self.scraping_thread = None
        self.stop_event = threading.Event()
        self.progress_queue = queue.Queue()
        self.results_queue = queue.Queue()
        self.delay_between_requests = 2
        self.max_pages = 10
        self.current_progress = 0
        
        self.driver = None
        self.playwright = None
        
        if driver is not None:
            print("WARNING: External driver passed - scraper should manage its own browser")

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
        """Stop scraping and cleanup"""
        self.stop_event.set()
        if self.scraping_thread:
            self.scraping_thread.join(timeout=5.0) 
    
    def _launch_browser(self):
        """Launch browser in the scraper's own thread with better error handling"""
        try:
            print("DEBUG: Launching browser in scraper thread...")
            pref_browser = getattr(self, 'preferred_browser', 'Chrome').lower()
            self.playwright = sync_playwright().start()
        
            launch_options = {
                'headless': False,
                'timeout': 30000,
                'args': ['--start-maximized']
            }
        
            browser_map = {
                'chrome': lambda: self.playwright.chromium.launch(channel="chrome", **launch_options),
                'firefox': lambda: self.playwright.firefox.launch(**launch_options),
                'microsoft edge': lambda: self.playwright.chromium.launch(channel="msedge", **launch_options),
                'edge': lambda: self.playwright.chromium.launch(channel="msedge", **launch_options),
                'safari': lambda: self.playwright.webkit.launch(**launch_options),
                'webkit': lambda: self.playwright.webkit.launch(**launch_options)
            }

            browser_key = pref_browser.lower()
            if browser_key not in browser_map:
                print(f"DEBUG: Browser '{pref_browser}' not found, falling back to chromium")
                browser_key = 'chrome'
        
            launcher = browser_map[browser_key]
            self.driver = launcher()
        
            print(f"DEBUG: {pref_browser} launched successfully: {self.driver.is_connected()}")
            return True
        
        except Exception as e:
            print(f"ERROR: Failed to launch {pref_browser}: {e}")

            try:
                print("DEBUG: Attempting fallback to Chromium...")
                if hasattr(self, 'playwright') and self.playwright:
                    self.driver = self.playwright.chromium.launch(
                        headless=False, 
                        timeout=30000
                    )
                    print("DEBUG: Fallback to Chromium successful")
                    return True
            except Exception as fallback_error:
                print(f"DEBUG: Fallback also failed: {fallback_error}")

        return False

    def _close_browser(self):
        """Close browser in the scraper's own thread"""
        try:
            if self.driver and self.driver.is_connected():
                self.driver.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            print(f"DEBUG: Browser cleanup warning: {e}")
        finally:
            self.driver = None
            self.playwright = None

    def _scrape_products(self, search_term, max_pages):
        """Main scraping logic - ALL in scraper thread"""
        try:
            if not self._launch_browser():
                error_msg = "Failed to launch browser in scraper thread"
                self._update_gui({'type': 'error', 'message': error_msg})
                return

            if not self.driver.is_connected():
                error_msg = "Browser not connected in scraper thread"
                self._update_gui({'type': 'error', 'message': error_msg})
                return

            print(f"DEBUG: Starting scrape in scraper thread")
            
            base_url = self._get_base_url(search_term)
            total_pages = min(max_pages, self.max_pages)

            for page_num in range(1, total_pages + 1):
                if self.stop_event.is_set():
                    print("DEBUG: Scraping stopped by stop_event")
                    break

                if not self.driver.is_connected():
                    error_msg = "Browser disconnected during scraping."
                    self._update_gui({'type': 'error', 'message': error_msg})
                    break

                self._update_progress(page_num - 1, total_pages)

                page_url = self._construct_page_url(base_url, search_term, page_num)
                if page_url == None:
                    print(f"DEBUG: No more pages to scrape, stopping at page {page_num-1}")
                    break
                
                print(f"DEBUG: Processing page {page_num}: {page_url}")

                search_page = self.driver.new_page()
                try:
                    product_links = self._extract_product_links(search_page, page_url)
                    print(f"DEBUG: Page {page_num}: Found {len(product_links)} product links")
                    
                    if not product_links:
                        print(f"DEBUG: No products found on page {page_num}")
                        break

                    for i, product_url in enumerate(product_links):
                        if self.stop_event.is_set():
                            break

                        if not self.driver.is_connected():
                            error_msg = "Browser disconnected during product processing."
                            self._update_gui({'type': 'error', 'message': error_msg})
                            break

                        self._update_progress(
                            (page_num - 1) + (i / len(product_links)),
                            total_pages
                        )

                        product_page = self.driver.new_page()
                        try:
                            print(f"DEBUG: Scraping product {i+1}/{len(product_links)}: {product_url}")
                            product_data = self._parse_product_page(product_page, product_url)
                            if product_data:
                                self._update_gui({"type": "product", 'data': product_data})
                                print(f"DEBUG: Successfully scraped product: {product_data.get('title', 'Unknown')}")
                            else:
                                print(f"DEBUG: Failed to scrape product: {product_url}")
                        finally:
                            if not product_page.is_closed():
                                product_page.close()

                        time.sleep(self.delay_between_requests * random.uniform(1, 2))
                
                finally:
                    if not search_page.is_closed():
                        search_page.close()

            self._update_progress(total_pages, total_pages)
            self._update_gui({'type': 'complete'})
            print("DEBUG: Scraping completed successfully")

        except Exception as e:
            print(f"DEBUG: Scraping error: {str(e)}")
            self._update_gui({'type': 'error', 'message': str(e)})
        finally:
            self._close_browser()
            self.stop_event.set()

    def _extract_and_convert_price(self, price_text):
        """Extract price from text and handle spaces in numbers"""
        try:
            if not price_text or price_text == "N/A":
                return 0.0
    
            print(f"DEBUG: Raw price text: '{price_text}'")
    
            # First, handle the specific AllStore case with newlines
            cleaned_text = ' '.join(price_text.split())  # Replace newlines with spaces
            print(f"DEBUG: Cleaned price text: '{cleaned_text}'")
    
            # Pattern for AllStore specific format: "196 85 лв" -> 196.85
            allstore_pattern = r'(\d+)\s+(\d+)\s*лв'
            allstore_match = re.search(allstore_pattern, cleaned_text)
            if allstore_match:
                whole_part = allstore_match.group(1)
                decimal_part = allstore_match.group(2)
                price_str = f"{whole_part}.{decimal_part}"
                price_value = float(price_str)
                print(f"DEBUG: AllStore format extracted: {price_value} from '{price_text}'")
                return price_value
    
            # Original patterns for other formats
            price_patterns = [
                r'(\d+(?:[.,]\d+)?)\s*лв',  
                r'€\s*(\d+(?:[.,]\d+)?)',   
                r'(\d+(?:[.,]\d+)?)\s*€',  
                r'\$?\s*(\d+(?:[.,]\d+)?)', 
            ]
    
            for pattern in price_patterns:
                match = re.search(pattern, cleaned_text)
                if match:
                    price_str = match.group(1)
                    price_str = price_str.replace(',', '.')
                    try:
                        price_value = float(price_str)
                        print(f"DEBUG: Extracted price '{price_str}' -> {price_value} from '{price_text}' using pattern '{pattern}'")
                        return price_value
                    except ValueError:
                        continue
    
            all_numbers = re.findall(r'\d+(?:[.,]\d+)?', cleaned_text)
            if all_numbers:
                numbers = []
                for num_str in all_numbers:
                    try:
                        clean_num = num_str.replace(',', '.').replace(' ', '')
                        num = float(clean_num)
                        if 0.1 < num < 100000:  
                            numbers.append(num)
                    except ValueError:
                        continue
        
                if numbers:
                    price_value = max(numbers)
                    print(f"DEBUG: Fallback extracted price: {price_value} from '{price_text}'")
                    return price_value
    
            print(f"DEBUG: No valid price found in: '{price_text}'")
            return 0.0
    
        except Exception as e:
            print(f"DEBUG: Price extraction error: {e} for text: '{price_text}'")
            return 0.0
    
    def generate_random_crid(self):
        """Generate random crid for Amazon URLs"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

    @abstractmethod
    def _get_base_url(self, search_term):
        """Website-specific search URL construction"""
        pass

    @abstractmethod
    def _construct_page_url(self, base_url, search_term, page):
        """Construct the URL for a specific page number"""
        pass

    @abstractmethod
    def _extract_product_links(self, page, page_url):
        """Extract product links from search page using Playwright"""
        pass

    @abstractmethod
    def _parse_product_page(self, page, product_url):
        """Parse product details using Playwright"""
        pass