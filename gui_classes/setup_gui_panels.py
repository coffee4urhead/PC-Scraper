import customtkinter as ctk

class PanelSetup:
    def __init__(self, master, settings_manager, bg_setup):
        self.master = master
        self.settings_manager = settings_manager
        self.bg_setup = bg_setup
        
    def create_panels(self):
        tabview = ctk.CTkTabview(self.master)
        tabview.pack(fill="both", expand=True)
        
        self.master.scraper_tab = tabview.add("Scraper")
        self.master.settings_tab = tabview.add("Settings")
        self.master.info_tab = tabview.add("Info")
        self.master.price_history_changes_tab = tabview.add("Price History changes")

        for tab in [self.master.scraper_tab, self.master.settings_tab, 
                   self.master.info_tab, self.master.price_history_changes_tab]:
            self.bg_setup.apply_background_to_tab(tab)

        self._create_main_panels()
        return tabview
    
    def _create_main_panels(self):
        self.master.left_panel = ctk.CTkFrame(
            self.master.scraper_tab, 
            width=500, 
            height=700, 
            fg_color=("#FFFFFF", "#1A1A1A"),
            border_width=2,
        )
        self.master.left_panel.place(x=30, y=35, relwidth=0.6, relheight=0.9)

        self.master.right_panel = ctk.CTkFrame(
            self.master.scraper_tab, 
            width=400, 
            height=700, 
            fg_color="#1A1A1A",  
            border_width=2,
            border_color=("#FFFFFF", "#1A1A1A"),
        )
        self.master.right_panel.place(x=770, y=35, relwidth=0.33, relheight=0.9)