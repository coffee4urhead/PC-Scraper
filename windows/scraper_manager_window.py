import customtkinter as ctk

class ScraperManagerWindow(ctk.CTkToplevel):
    def __init__(self, master=None, scraper_container=None):
        super().__init__(master)
        self.scraper_container = scraper_container  
        
        if hasattr(master, 'gui') and hasattr(master.gui, 'content_setup'):
            self.content_setup = master.gui.content_setup
        else:
            self.content_setup = master
            print("Warning: Could not find ContentSetup instance")


        self.geometry("520x820")
        self.title("🧩 Manage Active Scrapers")
        self.resizable(False, False)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=480, height=700)
        self.scroll_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the UI elements inside the scrollable frame"""
        
        active_frame = ctk.CTkFrame(self.scroll_frame)
        active_frame.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(
            active_frame,
            text="🟢 Active Scrapers",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        if self.scraper_container and self.scraper_container.scraper_list:
            for scraper in self.scraper_container.scraper_list:
                website = getattr(scraper, 'website_that_is_scraped', scraper.__class__.__name__)
                
                scraper_frame = ctk.CTkFrame(active_frame)
                scraper_frame.pack(fill="x", padx=20, pady=2)
                
                ctk.CTkLabel(
                    scraper_frame,
                    text=f"● {website}",
                    text_color="#00FF00"
                ).pack(side="left", padx=10)
                
                ctk.CTkButton(
                    scraper_frame,
                    text="Deactivate",
                    width=80,
                    height=25,
                    command=lambda w=website: self._deactivate_scraper(w)
                ).pack(side="right", padx=10)
        else:
            ctk.CTkLabel(
                active_frame,
                text="No active scrapers",
                text_color="gray"
            ).pack(pady=20)
        
        available_frame = ctk.CTkFrame(self.scroll_frame)
        available_frame.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(
            available_frame,
            text="📋 Available Websites",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        active_websites = []
        if self.scraper_container and self.scraper_container.scraper_list:
            active_websites = [
                getattr(s, 'website_that_is_scraped', s.__class__.__name__) 
                for s in self.scraper_container.scraper_list
            ]
        
        if hasattr(self.content_setup, 'website_options'):
            for website in self.content_setup.website_options:
                if website not in active_websites:
                    btn = ctk.CTkButton(
                        available_frame,
                        text=f"+ {website}",
                        command=lambda w=website: self._add_scraper(w),
                        fg_color="transparent",
                        border_width=1,
                        anchor="w",
                        height=30
                    )
                    btn.pack(fill="x", padx=20, pady=2)
        else:
            ctk.CTkLabel(
                available_frame,
                text="No websites available",
                text_color="gray"
            ).pack(pady=20)
    
    def _add_scraper(self, website):
        """Add a new scraper"""
        if hasattr(self.content_setup, '_get_website_selection_callback'):
            callback = self.content_setup._get_website_selection_callback()
            if callback:
                callback(website)
        self.destroy() 
        if hasattr(self.master, 'get_scraper_manager_window'):
            self.master.get_scraper_manager_window()
    
    def _deactivate_scraper(self, website):
        """Deactivate a scraper"""
        print(f"Deactivating scraper for {website} from manager")
    
        if hasattr(self.master, '_deactivate_scraper'):
            self.master._deactivate_scraper(website)
        else:
            print("ERROR: master has no _deactivate_scraper method")
    
        self.destroy()
        if hasattr(self.master, 'get_scraper_manager_window'):
            self.master.get_scraper_manager_window()    