from .base_scraper import AsyncPlaywrightBaseScraper
import asyncio
from typing import List, Dict, Any
import logging
import random
from playwright.async_api import async_playwright, Browser, BrowserContext

logger = logging.getLogger(__name__)

class ScraperContainer:
    def __init__(self, scraper_list: List[AsyncPlaywrightBaseScraper]):
        self.scraper_list = scraper_list
        self._active_scrapers = {}
        self._all_results = []
        self.browser = None
        self._playwright = None  
        self._contexts = {}

    async def start_shared_browser(self):
        """Start shared browser instances for all scrapers"""
        logger.info("Starting shared browsers for all scrapers...")
        try:
            self._playwright = await async_playwright().start()
            
            self.browser = await asyncio.shield(self._playwright.chromium.launch(
                headless=False,
                args=[
                    '--start-maximized',
                    '--disable-blink-features=AutomationControlled',
                ]
            ))

            logger.info("Shared browser and context started successfully.")
        except Exception as e:
            logger.error(f"Error starting shared browser: {e}")
            await self._cleanup_resources()
   
    async def _create_scraper_context(self, scraper) -> BrowserContext:
        """Create a unique context for each scraper"""
        viewports = [
            {'width': 1920, 'height': 1080},
            {'width': 1366, 'height': 768},
            {'width': 1536, 'height': 864},
            {'width': 1440, 'height': 900}
        ]

        user_agent = await self._get_random_user_agent()

        context = await self.browser.new_context(
            user_agent=user_agent,
            viewport=random.choice(viewports),
            locale='bg-BG',
            timezone_id='Europe/Sofia',
            color_scheme='light',
            reduced_motion='no-preference',
            java_script_enabled=True,
        )
        
        self._contexts[id(scraper)] = context

        return context
    async def start_all_scrapers_async(self, search_term: str, max_pages: int = 3) -> List[Dict[str, Any]]:
        """
        Start all scrapers concurrently using asyncio.
        Each scraper runs its own async start_scraping_async method.
        """
        self._all_results = []
        
        if not self.browser or not self.context:
            await self.start_shared_browser()
        
        scraper_tasks = []

        for scraper in self.scraper_list:
            context = await self._create_scraper_context(scraper)
            scraper.browser = self.browser
            scraper.context = context
            
            task = asyncio.create_task(
                self._run_single_scraper(scraper, search_term, max_pages)
            )
            scraper_tasks.append(task)
            self._active_scrapers[id(scraper)] = {
                'scraper': scraper,
                'task': task,
                'running': True
            }
        
        try:
            results = await asyncio.gather(*scraper_tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                scraper = self.scraper_list[i]
                if isinstance(result, Exception):
                    logger.error(f"Scraper {scraper.__class__.__name__} failed: {result}")
                elif result:
                    for product in result:
                        if product:
                            product['source_scraper'] = scraper.__class__.__name__
                            if hasattr(scraper, 'website_currency'):
                                product['source_currency'] = scraper.website_currency
                    self._all_results.extend(result)
            
            logger.info(f"All scrapers completed. Total products: {len(self._all_results)}")
            return self._all_results
            
        except Exception as e:
            logger.error(f"Error running scrapers: {e}")
            return self._all_results
        finally:
            await self._cleanup_contexts()
    
    async def _cleanup_contexts(self):
        """Clean up all contexts"""
        for scraper_id, context in self._contexts.items():
            try:
                await context.close()
                logger.debug(f"Closed context for scraper {scraper_id}")
            except Exception as e:
                logger.error(f"Error closing context for scraper {scraper_id}: {e}")
        self._contexts.clear()

    async def _cleanup_resources(self):
        """Clean up browser resources"""
        try:
            if self.context:
                await self.context.close()
                self.context = None
                logger.info("Browser context closed.")
        except Exception as e:
            logger.error(f"Error closing context: {e}")
        
        try:
            if self.browser:
                await self.browser.close()
                self.browser = None
                logger.info("Browser closed.")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
        
        try:
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
                logger.info("Playwright stopped.")
        except Exception as e:
            logger.error(f"Error stopping playwright: {e}")

    async def close_all_resources(self):
        """Public method to close all resources"""
        await self._cleanup_resources()

    async def _get_random_user_agent(self) -> str:
        """Get a random user agent for browser context"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        ]
        return random.choice(user_agents)
        
    async def _run_single_scraper(self, scraper: AsyncPlaywrightBaseScraper, 
                                  search_term: str, max_pages: int) -> List[Dict[str, Any]]:
        """
        Run a single scraper with proper error handling.
        """
        try:
            logger.info(f"Starting scraper: {scraper.__class__.__name__}")
            results = await scraper.start_scraping_async(search_term, max_pages)
            logger.info(f"Scraper {scraper.__class__.__name__} completed: {len(results)} products")
            return results
        except asyncio.CancelledError:
            logger.info(f"Scraper {scraper.__class__.__name__} was cancelled")
            return []
        except Exception as e:
            logger.error(f"Scraper {scraper.__class__.__name__} error: {e}")
            return []
        finally:
            scraper_id = id(scraper)
            if scraper_id in self._active_scrapers:
                self._active_scrapers[scraper_id]['running'] = False
            
    def stop_all_scrapers(self):
        """Stop all running scrapers"""
        logger.info("Stopping all scrapers...")
        stopped_count = 0
        
        for scraper_id, scraper_info in self._active_scrapers.items():
            scraper = scraper_info['scraper']
            task = scraper_info['task']
            
            if scraper.is_running():
                scraper.stop_scraping()
                stopped_count += 1
            
            if not task.done():
                task.cancel()
        
        logger.info(f"Stopped {stopped_count} scrapers")
        return stopped_count
        
    def get_scraper_status(self):
        """Get status of all scrapers"""
        status = {}
        for scraper in self.scraper_list:
            status[scraper.__class__.__name__] = {
                'running': scraper.is_running(),
                'progress': scraper.current_progress,
                'completed_tasks': scraper.completed_tasks,
                'total_tasks': scraper.total_tasks
            }
        return status
        
    def set_filter_for_all(self, min_price=None, max_price=None, exclude_keywords=""):
        """Apply filters to all scrapers"""
        for scraper in self.scraper_list:
            scraper.min_price = min_price
            scraper.max_price = max_price
            scraper.exclude_keywords = exclude_keywords
        logger.info(f"Filters applied to {len(self.scraper_list)} scrapers")
        
    def deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicate results from all scrapers by URL.
        If same product found by multiple scrapers, keep the first one.
        """
        seen_urls = set()
        deduplicated = []
        
        for product in results:
            if product and 'url' in product:
                if product['url'] not in seen_urls:
                    seen_urls.add(product['url'])
                    deduplicated.append(product)
        
        logger.info(f"Deduplicated {len(results)} -> {len(deduplicated)} products")
        return deduplicated
        
    def get_scraper_by_name(self, scraper_name: str) -> AsyncPlaywrightBaseScraper:
        """Get a scraper instance by its class name"""
        for scraper in self.scraper_list:
            if scraper.__class__.__name__ == scraper_name:
                return scraper
        return None