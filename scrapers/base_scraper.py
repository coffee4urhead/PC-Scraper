import asyncio
from abc import ABC, abstractmethod
from typing import Deque
import random
import re
import time 
from playwright.async_api import async_playwright
from typing import List, Dict, Any, Optional
import logging
from scrapers.cpu_memory_manager import CPUMemoryManagerClass
from settings_manager import SettingsManager
from currency_converter import RealCurrencyConverter
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AsyncPlaywrightBaseScraper(ABC):
    """Async version of the base scraper for massive performance gains"""
    
    def __init__(self, website_currency, gui_callback=None):
        self.website_currency = website_currency
        self.gui_callback = gui_callback
        self.converter = RealCurrencyConverter()
        self.settings_manager = SettingsManager()

        self.products_collected = 0
        self.total_expected_products = 0
    
        self.products_found_per_page = {}
        self.expected_products_per_page = {}

        self.max_concurrent_products = 3
        
        self._request_times = Deque()
        self.max_requests_per_minute = 30
        self.min_delay_between_requests = 1.5
        
        raw_min = self.settings_manager.get('min_price', 0)
        raw_max = self.settings_manager.get('max_price', 0)
        
        self.original_min_price = self._safe_float_conversion(raw_min, 0)
        self.original_max_price = self._safe_float_conversion(raw_max, float('inf'))
        
        self.preferred_currency = self.settings_manager.get('preferred_currency', "EUR")
        
        self.converted_min = self.original_min_price
        self.converted_max = self.original_max_price
        
        self._update_converted_prices()
        
        self.exclude_keywords = self.settings_manager.get('exclude_keywords', [])

        self.exclude_keywords = self.settings_manager.get('exclude_keywords', [])
        
        self.current_progress = 0
        self.total_tasks = 0
        self.completed_tasks = 0
        
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        ]
        self.cpu_manager = CPUMemoryManagerClass()
        self.process_pool = None
        
        self._stop_event = threading.Event()
        self._stop_requested = False
        self._active_tasks = []
        self._running = False

        self._processed_urls = set()

    def _update_converted_prices(self):
        """Update converted price values based on current settings"""
        target_currency = "EUR"
        
        if self.preferred_currency != target_currency:
            if self.original_min_price > 0:
                converted = self._convert_prices_only(self.original_min_price, self.preferred_currency, target_currency)
                self.converted_min = float(converted) if converted is not None else self.original_min_price
                print(f"DEBUG: Converted min_price to {self.converted_min} {target_currency}")
            else:
                self.converted_min = self.original_min_price
                
            if self.original_max_price != float('inf') and self.original_max_price > 0:
                converted = self._convert_prices_only(self.original_max_price, self.preferred_currency, target_currency)
                self.converted_max = float(converted) if converted is not None else self.original_max_price
                print(f"DEBUG: Converted max_price to {self.converted_max} {target_currency}")
            else:
                self.converted_max = self.original_max_price
        else:
            self.converted_min = self._convert_prices_only(self.original_min_price, "EUR", target_currency)
            self.converted_max = self._convert_prices_only(self.original_max_price, "EUR", target_currency)

    def convert_where_necessary(self, price):
        converted_price = float(self._convert_prices_only(price, self.website_currency, "EUR"))
        if converted_price is not None:
            if self._should_filter_by_price({'price': converted_price}):
                print(f'Skipped product because it was not in the range of the price filter: {self.converted_min:.2f} - {self.converted_max:.2f} EUR')
                return None
        else:
            print(f"DEBUG: Could not convert price {price} {self.website_currency} to EUR")

    def update_settings(self, min_price=None, max_price=None, exclude_keywords=None):
        """Update scraper settings and re-convert if needed"""
        updated = False
        
        if min_price is not None:
            self.original_min_price = float(min_price)
            updated = True
            
        if max_price is not None:
            self.original_max_price = float(max_price)
            updated = True
            
        if exclude_keywords is not None:
            self.exclude_keywords = exclude_keywords
            
        if updated:
            self._update_converted_prices()
            print(f"DEBUG: Updated settings - min: {self.original_min_price} -> {self.converted_min} {self.target_currency}, max: {self.original_max_price} -> {self.converted_max} {self.target_currency}")

    def _safe_float_conversion(self, value, default=0):
        """Safely convert any value to float"""
        if value is None:
            return default
            
        if isinstance(value, (int, float)):
            return float(value)
            
        if isinstance(value, str):
            try:
                cleaned = re.sub(r'[^\d.,-]', '', value)
                cleaned = cleaned.replace(',', '.')
                if cleaned.count('.') > 1:
                    parts = cleaned.split('.')
                    cleaned = parts[0] + '.' + ''.join(parts[1:])
                return float(cleaned) if cleaned else default
            except (ValueError, TypeError):
                return default
                
        return default
    def _convert_prices_only(self, price_val, source_currency, target_currency):
        """Convert a single price value to the target currency - returns float"""
        try:
            if isinstance(price_val, str):
                price_val = self._safe_float_conversion(price_val)
                
            if price_val is None:
                return None
                
            converted_price = self.converter.convert_currency(
                float(price_val),
                source_currency,
                target_currency
            )
            
            return float(converted_price) if converted_price is not None else None
            
        except Exception as e:
            print(f"Price conversion error: {str(e)}")
            return None
        
    async def _retry_operation(self, operation, operation_name, max_retries=3, initial_delay=2):
        """Generic retry decorator for any async operation"""
        for attempt in range(max_retries):
            try:
                result = await operation(attempt)
                if result is not None:  
                    return result
                
                if attempt < max_retries - 1:
                    delay = initial_delay * (attempt + 1)
                    print(f"DEBUG: {operation_name} returned None, retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    continue
                    
            except Exception as e:
                print(f"DEBUG: {operation_name} attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:  
                    delay = initial_delay * (attempt + 1)
                    print(f"DEBUG: Retrying {operation_name} in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    print(f"DEBUG: All attempts failed for {operation_name}")
                    import traceback
                    traceback.print_exc()
        
        return None  
    
    async def _navigate_with_retry(self, page, url: str, attempt: int) -> bool:
        """Navigate to URL with retry logic"""
        await page.mouse.wheel(0, random.randint(400, 900))
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        wait_strategies = ['domcontentloaded', 'load', 'networkidle']
        wait_strategy = wait_strategies[min(attempt, len(wait_strategies)-1)]
        
        await page.goto(url, wait_until=wait_strategy, timeout=30000)
        print(f"DEBUG: Page loaded successfully: {url} (wait_until: {wait_strategy})")
        return True
    
    async def _wait_for_selector_with_fallback(self, page, selectors: List[str], timeout: int = 10000) -> Optional[str]:
        """Wait for any of the given selectors with fallback options"""
        for selector in selectors:
            try:
                await page.wait_for_selector(selector, timeout=timeout)
                print(f"DEBUG: Found selector: {selector}")
                return selector
            except Exception:
                continue
        return None
    
    async def _rate_limit(self):
        """Rate limiting to avoid detection"""
        now = time.time()
    
        while self._request_times and now - self._request_times[0] > 60:
            self._request_times.popleft()
        
        if len(self._request_times) >= self.max_requests_per_minute:
            wait_time = 60 - (now - self._request_times[0])
            if wait_time > 0:
                print(f"DEBUG: Rate limit hit, waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
        
        delay = self.settings_manager.get('delay_between_requests', 2) * random.uniform(0.8, self.settings_manager.get('random_delay_multiplier', 1.5))
        delay = max(delay, self.min_delay_between_requests)
        
        print(f"DEBUG: Rate limiting - waiting {delay:.2f}s")
        await asyncio.sleep(delay)
        
        self._request_times.append(now)
    
    async def _get_random_user_agent(self):
        """Get random user agent"""
        return random.choice(self.user_agents)
    
    def stop_scraping(self):
        """Stop this individual scraper instance"""
        print(f"🛑 Stopping scraper: {self.__class__.__name__}")
    
        self._stop_requested = True
        self._running = False

        if hasattr(self, '_stop_event'):
            self._stop_event.set()
    
        if hasattr(self, '_active_tasks') and self._active_tasks:
            for task in self._active_tasks:
                if not task.done():
                    task.cancel()
            self._active_tasks.clear()
    
        self._update_gui({
            'type': 'status',
            'message': f'Stopped scraper: {self.__class__.__name__}'
        })
    
        return 1
    
    def is_running(self):
        """Check if scraping is running"""
        return self._running
    
    async def start_scraping_async(self, search_term: str, max_pages: int = 3) -> List[Dict[str, Any]]:
        """Main async scraping entry point"""
        try:
            self._stop_requested = False
            self._stop_event.clear()
            self._running = True
            self._active_tasks = []
            self.current_progress = 0
            self.completed_tasks = 0
            self.total_pages_to_scrape = 0
            self.total_products_found = 0
            self.products_per_page = {}
            
            self._update_gui({
                'type': 'product_count',
                'total_found': 0,
                'page_products': 0,
                'page_num': 0,
                'scraper_name': self.__class__.__name__
            })
            self._update_gui({'type': 'start', 'scraper_name' : self.__class__.__name__, 'message': 'Starting async scrape'})
            
            optimal_workers = self.cpu_manager.get_optimal_worker_count()
            logger.info(f"Using {optimal_workers} workers for scraping")

            all_results = await self._distributed_scrape(search_term, max_pages, optimal_workers)
            
            self._running = False
            if not self._stop_requested:
                self._update_gui({'type': 'complete', 'results': len(all_results)})
            else:
                self._update_gui({
                    'type': 'status', 
                    'message': f'Scraping stopped. Collected {len(all_results)} products.'
                })
            
            return all_results
            
        except asyncio.CancelledError:
            logger.info("Scraping cancelled")
            self._running = False
            self._update_gui({'type': 'status', 'message': 'Scraping cancelled'})
            return []
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            self._running = False
            self._update_gui({'type': 'error', 'message': str(e)})
            return []

    async def _cleanup_scraper_resources(self):
        """Clean up scraper-specific resources"""
        try:
            if hasattr(self, '_context') and self._context:
                await self._context.close()
                self._context = None
                logger.debug("Scraper context closed")
        except Exception as e:
            logger.error(f"Error closing scraper context: {e}")

    async def _distributed_scrape(self, search_term: str, max_pages: int, num_workers: int) -> List[Dict[str, Any]]:
        """Distribute scraping across multiple processes/cores with stop support"""
        
        worker_tasks = []
        self.total_pages_to_scrape = 0

        for worker_id in range(1):
            start_page = worker_id * self.settings_manager.get('max_pages', 1) + 1
            end_page = min((worker_id + 1) * self.settings_manager.get('max_pages', 2), max_pages)
            
            if start_page <= end_page:
                pages_in_this_worker = end_page - start_page + 1
                self.total_pages_to_scrape += pages_in_this_worker

                task = asyncio.create_task(
                    self._worker_scrape(search_term, start_page, end_page, worker_id)
                )
                task._shielded = True
                worker_tasks.append(task)
                self._active_tasks.append(task)
                print(f"📊 Total pages to scrape: {self.total_pages_to_scrape}")
        try:
            worker_results = await asyncio.gather(*worker_tasks, return_exceptions=True)
        
            all_results = []
            for result in worker_results:
                if isinstance(result, Exception):
                    logger.error(f"Worker failed: {result}")
                elif result:
                    all_results.extend(result)
            
            return all_results
            
        except asyncio.CancelledError:
            logger.info("Tasks cancelled")
            if worker_tasks:
                done, pending = await asyncio.wait(
                    worker_tasks,
                    timeout=10.0,  
                    return_when=asyncio.ALL_COMPLETED
                )

                for task in pending:
                    if not task.done() and not getattr(task, '_shielded', False):
                        task.cancel()
                
            raise
    
    async def _worker_scrape(self, search_term: str, start_page: int, end_page: int, worker_id: int) -> List[Dict[str, Any]]:
        """Single worker scraping a range of pages with stop support"""
        results = []

        if self._stop_requested:
            logger.info(f"Worker {worker_id}: Stop requested before start")
            return []

        self.cpu_manager.set_worker_affinity(worker_id)
    
        try:
            if not hasattr(self, 'context') or not self.context:
                logger.error(f"Worker {worker_id}: No context available")
                return []
        
            context = self.context
        
            for page_num in range(start_page, end_page + 1):
                if self._stop_requested or self._stop_event.is_set():
                    logger.info(f"Worker {worker_id}: Stop requested at page {page_num}")
                    break
            
                page_results = await asyncio.shield(self._scrape_single_page_async(
                    context, search_term, page_num, worker_id
                ))

                if page_results:
                    results.extend(page_results)

                if self._stop_requested:
                    break
                
                self._update_gui({
                    'type': 'product_progress',
                    'collected': self.products_collected,  
                    'total_expected': self.total_expected_products,
                    'page_num': page_num,
                    'scraper_name': self.__class__.__name__
                })
                if not self._stop_requested:
                    try:
                        await asyncio.wait_for(
                            asyncio.sleep(self.settings_manager.get('delay_between_requests', 2) * random.uniform(0.8, 1.2)),
                            timeout=5.0
                        )
                    except asyncio.TimeoutError:
                        pass  
        
            return results

        except asyncio.CancelledError:
            logger.info(f"Worker {worker_id} cancelled")
            return results
        except Exception as e:
            logger.error(f"Worker {worker_id} failed: {e}")
            return results

    async def _scrape_single_page_async(self, context, search_term: str, page_num: int, worker_id: int) -> List[Dict[str, Any]]:
        if self._stop_requested:
            return []

        await self._rate_limit()

        page_url = self._construct_page_url(
            self._get_base_url(search_term),
            search_term,
        )

        if not page_url:
            logger.warning(f"Worker {worker_id}: No URL for page {page_num}")
            return []

        logger.info(f"Worker {worker_id}: Scraping page {page_num}: {page_url}")

        links_page = None
        try:
            links_page = await context.new_page()
            links_page.set_default_timeout(60000)
            await links_page.goto(page_url, wait_until="domcontentloaded", timeout=30000)

            if self._stop_requested:
                await links_page.close()
                return []

            await asyncio.sleep(random.uniform(1.5, 3.0))

            product_links = await self._extract_product_links_async(links_page, page_url)
            products_on_page = len(product_links)

            self.products_per_page[page_num] = products_on_page

            self.total_expected_products = sum(self.products_per_page.values())

            self._update_gui({
                'type': 'total_updated',
                'total_expected': self.total_expected_products,  
                'page_num': page_num,
                'page_products': products_on_page,
                'scraper_name': self.__class__.__name__
            })
            await links_page.evaluate("window.scrollTo(0, Math.random() * 500)")
            await asyncio.sleep(random.uniform(0.5, 1.5))
            await links_page.close()
            
            if not product_links:
                logger.warning(f"Worker {worker_id}: No products found on page {page_num}")
                return []

            logger.info(
                f"Worker {worker_id}: Found {len(product_links)} products on page {page_num}"
            )

            semaphore = asyncio.Semaphore(self.max_concurrent_products)

            async def scrape_with_delay(product_url: str):
                async with semaphore:
                    if self._stop_requested:
                        return None

                    await asyncio.sleep(random.uniform(2.5, 5.0))
                
                    product_page = await context.new_page()
                    product_page.set_default_timeout(60000)
                
                    try:
                        result = await self._scrape_single_product_async(
                            product_page, product_url, worker_id
                        )
                        return result
                    finally:
                        try:
                            await product_page.close()
                        except:
                            pass

            tasks = [
                scrape_with_delay(url)
                for url in product_links
                if not self._stop_requested
            ]

            try:
                product_results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=300.0
                )
            except asyncio.TimeoutError:
                logger.warning(f"Worker {worker_id}: Page {page_num} timed out")
                return []

            valid_results = []

            for result in product_results:
                if isinstance(result, Exception):
                    if not isinstance(result, asyncio.CancelledError):
                        logger.error(f"Product scraping error: {result}")
                elif result:
                    valid_results.append(result)

            return valid_results

        except asyncio.CancelledError:
            logger.info(f"Worker {worker_id}: Page {page_num} cancelled")
            return []

        except Exception as e:
            logger.error(f"Worker {worker_id}: Error scraping page {page_num}: {e}")
            return []

    async def _scrape_single_product_async(self, page, product_url: str, worker_id: int):
        """Scrape a single product asynchronously with stop support and reduced page reloads."""

        if self._stop_requested:
            return None

        await self._rate_limit()

        for attempt in range(3):
            if self._stop_requested:
                return None

            try:
                await page.goto(product_url, wait_until='domcontentloaded', timeout=15000)
                break  
            except Exception as e:
                if attempt == 2:
                    logger.error(f"Worker {worker_id}: Failed to load {product_url}: {e}")
                    return None
                await asyncio.sleep(1 * (attempt + 1))
        else:
            return None

        if self._stop_requested:
            return None

        try:
            product_data = await self._extract_product_data_async(page, product_url)
            if self.update_gui_callback:
                self.update_gui_callback({'type': 'product', 'data': product_data})

            if self._stop_requested or not product_data:
                return None

            product_data['url'] = product_url
        
            if product_data:
                self.products_collected += 1
                self._update_gui({"type": "product", 'data': product_data})

                self._update_gui({
                    'type': 'product_progress',
                    'collected': self.products_collected,
                    'total_expected': self.total_expected_products,
                    'product_title': product_data.get('title', '')[:30],
                    'scraper_name': self.__class__.__name__
                })
                return product_data

            return None

        except asyncio.CancelledError:
            logger.debug(f"Worker {worker_id}: Product scraping cancelled for {product_url}")
            return None
        except Exception as e:
            logger.error(f"Worker {worker_id}: Error scraping {product_url}: {e}")
            return None

    
    async def _extract_product_links_async(self, page, page_url: str) -> List[str]:
        """Async version of product link extraction"""
        try:
            return await self._extract_product_links(page, page_url)
        except Exception as e:
            logger.error(f"Error extracting product links from {page_url}: {e}")
            self._retry_operation(self._extract_product_links, "extract_product_links", max_retries=3)
            return []

    async def _extract_product_data_async(self, page, product_url: str) -> Optional[Dict[str, Any]]:
        """Async version of product data extraction"""
        try:
            return await self._extract_product_data(page, product_url)
        except Exception as e:
            logger.error(f"Error extracting product data from {product_url}: {e}")
            self._retry_operation(self._extract_product_data, "extract_product_data", max_retries=3)
            return None
    
    def _should_include_product(self, product_data: Dict[str, Any]) -> bool:
        """Check if product passes all filters"""
        return not (self._should_filter_by_price(product_data) or 
                   self._should_filter_by_keywords(product_data))
    
    def _update_gui(self, data):
        """Update GUI callback if available"""
        if self.gui_callback:
            try:
                self.gui_callback(data)
            except:
                pass

    def _should_filter_by_price(self, product_data):
        """Check if product should be filtered based on price settings"""
        price = product_data.get('price', 0)
        
        try:
            if self.converted_min and price < float(self.converted_min):
                return True
            if self.converted_max and price > float(self.converted_max):
                return True
        except (ValueError, TypeError):
            logger.debug(f"Invalid price filter values - min: {self.converted_min}, max: {self.converted_max}")
            
        return False

    def _should_filter_by_keywords(self, product_data):
        """Check if product should be filtered based on excluded keywords"""
        if not self.exclude_keywords:
            return False

        if isinstance(self.exclude_keywords, str):
            excluded_words = [word.strip().lower() for word in self.exclude_keywords.split(',') if word.strip()]
        else:
            excluded_words = [word.lower() for word in self.exclude_keywords if word]
    
        title = product_data.get('title', '').lower()
        description = product_data.get('description', '').lower()
    
        logger.debug(f"Filter check - Title: '{title}'")
        logger.debug(f"Filter check - Excluded: {excluded_words}")
    
        def super_normalize(text):
            text = re.sub(r'[®™©]', '', text)  
            text = text.replace('-', ' ')       
            text = re.sub(r'\s+', ' ', text)   
            text = text.replace('core', '').replace('intel', '').strip()  
            return text
    
        normalized_title = super_normalize(title)
        normalized_description = super_normalize(description)
    
        logger.debug(f"Filter check - Normalized title: '{normalized_title}'")
    
        for excluded_word in excluded_words:
            normalized_excluded = super_normalize(excluded_word)
        
            if (normalized_excluded in normalized_title or 
                normalized_excluded in normalized_description):
                logger.debug(f"FILTERED - Excluded: '{excluded_word}', Title: '{title}'")
                return True
        
            if (excluded_word in title or excluded_word in description):
                logger.debug(f"FILTERED - Excluded: '{excluded_word}', Title: '{title}'")
                return True
    
        return False
    
    @abstractmethod
    def _get_base_url(self, search_term):
        """Website-specific search URL construction"""
        pass

    @abstractmethod
    def _construct_page_url(self, base_url, search_term):
        """Construct the URL for a specific page number"""
        pass

    @abstractmethod
    async def _extract_product_links(self, page, page_url):
        """Extract product links from search page using Playwright"""
        pass
    
    @abstractmethod
    async def _extract_product_data(self, page, product_url):
        """Subclasses must implement this - extract raw product data without filtering"""
        pass