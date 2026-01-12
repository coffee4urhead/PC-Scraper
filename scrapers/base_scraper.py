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
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AsyncPlaywrightBaseScraper(ABC):
    """Async version of the base scraper for massive performance gains"""
    
    def __init__(self, website_currency, gui_callback=None):
        self.website_currency = website_currency
        self.gui_callback = gui_callback
        
        self.max_concurrent_pages = 2
        self.max_concurrent_products = 3
        self.delay_between_requests = 2
        self.random_delay_multiplier = 1.5
        
        self._request_times = Deque()
        self.max_requests_per_minute = 30  
        self.min_delay_between_requests = 1.5 
        self.preferred_browser = "chrome"
        self.headless = True  
        
        self.min_price = None
        self.max_price = None
        self.exclude_keywords = ""
        
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
        
        delay = self.delay_between_requests * random.uniform(0.8, self.random_delay_multiplier)
        delay = max(delay, self.min_delay_between_requests)
        
        print(f"DEBUG: Rate limiting - waiting {delay:.2f}s")
        await asyncio.sleep(delay)
        
        self._request_times.append(now)
    
    async def _get_random_user_agent(self):
        """Get random user agent"""
        return random.choice(self.user_agents)
    
    def stop_scraping(self):
        """Stop the scraping process"""
        logger.info("Stop requested")
        self._stop_requested = True
        self._stop_event.set()
        
        for task in self._active_tasks:
            if not task.done():
                task.cancel()
        
        self._update_gui({
            'type': 'status', 
            'message': 'Scraping stopped by user'
        })
        
        self._running = False
        return True
    
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
            
            self._update_gui({'type': 'start', 'message': 'Starting async scrape'})
            
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
    
    async def _distributed_scrape(self, search_term: str, max_pages: int, num_workers: int) -> List[Dict[str, Any]]:
        """Distribute scraping across multiple processes/cores with stop support"""
        
        pages_per_worker = max(1, max_pages // num_workers)
        worker_tasks = []
        
        for worker_id in range(num_workers):
            start_page = worker_id * pages_per_worker + 1
            end_page = min((worker_id + 1) * pages_per_worker, max_pages)
            
            if start_page <= end_page:
                task = asyncio.create_task(
                    self._worker_scrape(search_term, start_page, end_page, worker_id)
                )
                worker_tasks.append(task)
                self._active_tasks.append(task)
        
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
            for task in worker_tasks:
                if not task.done():
                    task.cancel()
            raise
    
    async def _worker_scrape(self, search_term: str, start_page: int, end_page: int, worker_id: int) -> List[Dict[str, Any]]:
        """Single worker scraping a range of pages with stop support"""
        
        if self._stop_requested:
            logger.info(f"Worker {worker_id}: Stop requested before start")
            return []
        
        self.cpu_manager.set_worker_affinity(worker_id)
    
        browser = None
        results = []
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=self.headless,
                    args=[
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-gpu'
                    ]
                )
                
                for page_num in range(start_page, end_page + 1):
                    if self._stop_requested or self._stop_event.is_set():
                        logger.info(f"Worker {worker_id}: Stop requested at page {page_num}")
                        break
                    
                    page_results = await self._scrape_single_page_async(
                        browser, search_term, page_num, worker_id
                    )
                    results.extend(page_results)
                    
                    if self._stop_requested:
                        break
                    
                    if not self._stop_requested:
                        self.completed_tasks += 1
                        if self.total_tasks > 0:
                            progress = int((self.completed_tasks / self.total_tasks) * 100)
                            if progress > self.current_progress:
                                self.current_progress = progress
                                self._update_gui({'type': 'progress', 'value': progress})
                    
                    if not self._stop_requested:
                        try:
                            await asyncio.wait_for(
                                asyncio.sleep(self.delay_between_requests * random.uniform(0.8, 1.2)),
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
        finally:
            if browser:
                await browser.close()
    
    async def _scrape_single_page_async(self, browser, search_term: str, page_num: int, worker_id: int) -> List[Dict[str, Any]]:
        """Scrape a single page and all its products concurrently with stop support"""
        
        if self._stop_requested:
            return []
        
        await self._rate_limit()
        page_url = self._construct_page_url(self._get_base_url(search_term), search_term, page_num)
        if not page_url:
            logger.warning(f"Worker {worker_id}: No URL for page {page_num}")
            return []
        
        logger.info(f"Worker {worker_id}: Scraping page {page_num}: {page_url}")
        
        user_agent = await self._get_random_user_agent()
        context = await browser.new_context(
            user_agent=user_agent,
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='Europe/Sofia',
            permissions=[],
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            }
        )
        
        try:
            page = await context.new_page()

            await page.goto(page_url, wait_until='domcontentloaded', timeout=30000)
            
            if self._stop_requested:
                return []
            
            product_links = await self._extract_product_links_async(page, page_url)
            
            if not product_links:
                logger.warning(f"Worker {worker_id}: No products found on page {page_num}")
                return []
            
            logger.info(f"Worker {worker_id}: Found {len(product_links)} products on page {page_num}")
            
            product_tasks = []
            for product_url in product_links:
                if self._stop_requested:
                    break
                
                task = asyncio.create_task(
                    self._scrape_single_product_async(browser, product_url, worker_id)
                )
                product_tasks.append(task)
                self._active_tasks.append(task)

            semaphore = asyncio.Semaphore(self.max_concurrent_products)
            
            async def limited_task(task):
                async with semaphore:
                    if self._stop_requested:
                        return None
                    return await task
            
            limited_tasks = [limited_task(task) for task in product_tasks]
            
            try:
                product_results = await asyncio.wait_for(
                    asyncio.gather(*limited_tasks, return_exceptions=True),
                    timeout=120.0  
                )
            except asyncio.TimeoutError:
                logger.warning(f"Worker {worker_id}: Page {page_num} timed out")
                for task in product_tasks:
                    if not task.done():
                        task.cancel()
                product_results = []
            
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
        finally:
            await context.close()
    
    async def _scrape_single_product_async(self, browser, product_url: str, worker_id: int) -> Optional[Dict[str, Any]]:
        """Scrape a single product asynchronously with stop support"""
        
        if self._stop_requested:
            return None
        
        await self._rate_limit()
        context = await browser.new_context()
        
        try:
            page = await context.new_page()
            
            if self._stop_requested:
                return None
            
            for attempt in range(3):
                try:
                    if self._stop_requested:
                        return None
                    
                    await page.goto(product_url, wait_until='domcontentloaded', timeout=15000)
                    break
                except Exception as e:
                    if attempt == 2:
                        logger.error(f"Worker {worker_id}: Failed to load {product_url}: {e}")
                        return None
                    if self._stop_requested:
                        return None
                    await asyncio.sleep(1 * (attempt + 1))
            
            if self._stop_requested:
                return None
            
            product_data = await self._extract_product_data_async(page, product_url)
            
            if self._stop_requested:
                return None
            
            if product_data and self._should_include_product(product_data):
                self._update_gui({"type": "product", 'data': product_data})
                return product_data
            
            return None
            
        except asyncio.CancelledError:
            logger.debug(f"Worker {worker_id}: Product scraping cancelled for {product_url}")
            return None
        except Exception as e:
            logger.error(f"Worker {worker_id}: Error scraping {product_url}: {e}")
            return None
        finally:
            await context.close()
    
    async def _extract_product_links_async(self, page, page_url: str) -> List[str]:
        """Async version of product link extraction"""
        return await self._extract_product_links(page, page_url)
    
    async def _extract_product_data_async(self, page, product_url: str) -> Optional[Dict[str, Any]]:
        """Async version of product data extraction"""
        return await self._extract_product_data(page, product_url)
    
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
            if self.min_price and price < float(self.min_price):
                return True
            if self.max_price and price > float(self.max_price):
                return True
        except (ValueError, TypeError):
            logger.debug(f"Invalid price filter values - min: {self.min_price}, max: {self.max_price}")
            
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
    def _construct_page_url(self, base_url, search_term, page):
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