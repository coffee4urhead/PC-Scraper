from scrapers.amazon_com_scraper import AmazonComScraper
from scrapers.ardes_scraper import ArdesScraper
from scrapers.jar_computers_scraper import JarComputersScraper
from scrapers.desktop_bg_scraper import DesktopScraper
from scrapers.plasico_scraper import PlasicoScraper
from scrapers.xtreme_bg_scraper import XtremeScraper
from scrapers.all_store_bg_scraper import AllStoreScraper
from scrapers.pc_tech_scraper import PcTechBgScraper
from scrapers.cyber_trade_scraper import CyberTradeScraper
from scrapers.pic_bg_scraper import PICBgScraper
from scrapers.hits_bg_scraper import HitsBGScraper
from scrapers.tehnik_store_scraper import TehnikStoreScraper
from scrapers.pro_bg_scraper import ProBgScraper
from scrapers.tova_bg_scraper import TovaBGScraper
from scrapers.senetic_scraper import SeneticScraper
from scrapers.gt_computers import GtComputersScraper
from scrapers.techno_mall_scraper import TechnoMallScraper
from scrapers.thnx_bg_scraper import ThxScraper
from scrapers.amazon_co_uk_scraper import AmazonCoUkScraper
from scrapers.ezona_bg_scraper import EZonaScraper
from scrapers.amazon_de_scraper import AmazonDeScraper
from scrapers.optimal_computers_scraper import OptimalComputersScraper

class ScraperManager:
    """Manages scraper instantiation and configuration"""
    
    def __init__(self, master, settings_manager):
        self.master = master
        self.settings_manager = settings_manager
        self.current_scraper = None
        
        self.website_currency_map = {
            "Amazon.com": "USD",
            "Ardes.bg": "BGN",
            "jarcomputers.com": "BGN",
            "Desktop.bg": "BGN",
            "Plasico.bg": "BGN",
            "PIC.bg": "BGN",
            "Optimal Computers": "BGN",
            "Xtreme.bg": "BGN",
            "CyberTrade.bg": "BGN",
            "PcTech.bg": "EUR",
            "Pro.bg": "BGN",
            "TechnoMall.bg": "BGN",
            "TehnikStore.bg": "BGN",
            "AllStore.bg": "EUR",
            "Senetic.bg": "BGN",
            "Thx.bg": "BGN",
            "GtComputers.bg": "EUR",
            "Ezona.bg": "BGN",
            "Tova.bg": "BGN",
            "Hits.bg": "EUR",
            "Amazon.co.uk": "GBP",
            "Amazon.de": "EUR"
        }
    
    def instantiate_scraper(self, website_name):
        """Instantiate the appropriate scraper based on website selection"""
        print(f"DEBUG: Initializing scraper for {website_name}")
        
        try:
            currency = self.website_currency_map.get(website_name, "BGN")
            
            if website_name == "Amazon.com":
                scraper = AmazonComScraper(currency, self.master.update_gui)
            elif website_name == "Ardes.bg":
                scraper = ArdesScraper(currency, self.master.update_gui)
            elif website_name == 'jarcomputers.com':
                scraper = JarComputersScraper(currency, self.master.update_gui)
            elif website_name == "Desktop.bg":
                scraper = DesktopScraper(currency, self.master.update_gui)
            elif website_name == "Plasico.bg":
                scraper = PlasicoScraper(currency, self.master.update_gui)
            elif website_name == "PIC.bg":
                scraper = PICBgScraper(currency, self.master.update_gui)
            elif website_name == "Optimal Computers":
                scraper = OptimalComputersScraper(currency, self.master.update_gui)
            elif website_name == "Xtreme.bg":
                scraper = XtremeScraper(currency, self.master.update_gui)
            elif website_name == "CyberTrade.bg":
                scraper = CyberTradeScraper(currency, self.master.update_gui)
            elif website_name == "PcTech.bg":
                scraper = PcTechBgScraper(currency, self.master.update_gui)
            elif website_name == "Pro.bg":
                scraper = ProBgScraper(currency, self.master.update_gui)
            elif website_name == "TechnoMall.bg":
                scraper = TechnoMallScraper(currency, self.master.update_gui)
            elif website_name == "TehnikStore.bg":
                scraper = TehnikStoreScraper(currency, self.master.update_gui)
            elif website_name == "AllStore.bg":
                scraper = AllStoreScraper(currency, self.master.update_gui)
            elif website_name == "Senetic.bg":
                scraper = SeneticScraper(currency, self.master.update_gui)
            elif website_name == "Thx.bg":
                scraper = ThxScraper(currency, self.master.update_gui)
            elif website_name == "GtComputers.bg":
                scraper = GtComputersScraper(currency, self.master.update_gui)
            elif website_name == "Ezona.bg":
                scraper = EZonaScraper(currency, self.master.update_gui)
            elif website_name == "Tova.bg":
                scraper = TovaBGScraper(currency, self.master.update_gui)
            elif website_name == "Hits.bg":
                scraper = HitsBGScraper(currency, self.master.update_gui)
            elif website_name == "Amazon.co.uk":
                scraper = AmazonCoUkScraper(currency, self.master.update_gui)
            elif website_name == "Amazon.de":
                scraper = AmazonDeScraper(currency, self.master.update_gui)
            else:
                raise ValueError(f"Unknown website: {website_name}")
            
            self._apply_settings_to_scraper(scraper)  
            self.current_scraper = scraper
            
            print(f"DEBUG: Scraper created successfully for {website_name}")
            return scraper
            
        except Exception as e:
            print(f"DEBUG: Scraper initialization failed: {e}")
            self.master.update_gui(f"Error creating scraper: {str(e)}", level="error")
            return None
    def _apply_settings_to_scraper(self, scraper):
        """Apply settings directly to an individual scraper"""
        if not scraper or not self.settings_manager:
            return
    
        try:
            scraper_settings = {k: v for k, v in self.settings_manager.settings.items() 
                            if k != 'ui_settings'}
        
            for key, value in scraper_settings.items():
                try:
                    if hasattr(scraper, key):
                        setattr(scraper, key, value)
                    else:
                        scraper.__dict__[key] = value
                except Exception as e:
                    print(f"⚠️ Error setting {key} on scraper {scraper.__class__.__name__}: {e}")
        
            print(f"✅ Applied settings to {scraper.__class__.__name__}")
        
        except Exception as e:
            print(f"❌ Error applying settings to scraper: {e}")

    def get_current_scraper(self):
        """Get the current active scraper"""
        return self.current_scraper
    
    def cleanup(self):
        """Clean up scraper resources if needed"""
        if self.current_scraper and hasattr(self.current_scraper, 'cleanup'):
            self.current_scraper.cleanup()
        self.current_scraper = None