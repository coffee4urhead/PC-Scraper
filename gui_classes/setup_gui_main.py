import customtkinter as ctk
from .setup_gui_background import BackgroundSetup
from .setup_gui_panels import PanelSetup
from .setup_gui_content import ContentSetup
from .setup_gui_settings import SettingsTabSetup
from .gui_state_manager import GUIStateManager
from scrapers.scraper_container_class import ScraperContainer
from .scraper_manager import ScraperManager
from settings_manager import SettingsManager
import os
import sys
import json

def resource_path(relative_path): 
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else: 
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class SetupGUI:
    def __init__(self, master=None):
        self.master = master
        if not hasattr(self.master, 'settings_manager'):
            self.master.settings_manager = SettingsManager()
        
        self.master.setup_gui_instance = self 
        self.master.tab_backgrounds = []
        self.part_options = ["Motherboard", 'PSU', 'RAM', 'GPU', 'Case', 'Fans', 'CPU', 'AIO', 
                           'Air Coolers', 'Extension Cables', 'HDD', 'SATA SSD', 'NVME SSD']
        self.website_options = ['Ardes.bg', 'AllStore.bg', 'Amazon.co.uk', 'Hits.bg', 'Tova.bg', 
                              'Ezona.bg', 'GtComputers.bg', 'Thx.bg', 'Senetic.bg', 'TehnikStore.bg', 
                              'Pro.bg', 'TechnoMall.bg', 'PcTech.bg', 'CyberTrade.bg', 'Xtreme.bg', 
                              'Optimal Computers', 'Plasico.bg', 'PIC.bg', 'jarcomputers.com', 
                              'Desktop.bg', 'Amazon.com', 'Amazon.de']
        
        self._load_settings()
        
        theme_path = self.master.settings_manager.get_theme_path()
        ctk.set_default_color_theme(theme_path) 
        ctk.set_appearance_mode(self.master.settings_manager.get_ui_setting('preferred_theme', 'system').lower())
        
        self._setup_components()
    
    def _load_settings(self):
        """Load all settings from settings manager"""
        self.master.preferred_currency = self.master.settings_manager.get('preferred_currency', 'BGN')
        self.master.price_format = self.master.settings_manager.get('price_format', '0.00')
        self.master.currency_symbol = "лв"
        self.master.preferred_language = self.master.settings_manager.get_ui_setting('preferred_language', 'en-US')
        self.master.preferred_size = int(self.master.settings_manager.get_ui_setting('preferred_size', 16))
        self.master.preferred_browser = self.master.settings_manager.get('preferred_browser', 'Chrome')
        self.master.preferred_theme = self.master.settings_manager.get_ui_setting('preferred_theme', 'system')
        self.master.preferred_font = self.master.settings_manager.get_ui_setting('preferred_font', 'Verdana')
        self.master.save_folder = self.master.settings_manager.get_ui_setting('save_folder', 
                                                                             os.path.join(os.path.expanduser("~"), "Desktop"))
        self.master.primary_color = self.master.settings_manager.get_ui_setting('primary_color', '#3B8ED0')
        self.master.secondary_color = self.master.settings_manager.get_ui_setting('secondary_color', '#1F6AA5')
        self.master.selected_pc_part = "GPU"
        self.master.first_website_for_comparison = self.master.settings_manager.get('first_website_for_comparison', 'Ardes,bg')
        self.master.second_website_for_comparison = self.master.settings_manager.get('second_website_for_comparison', 'Desktop.bg')
        self.master.part_to_compare_historically = 'GPU'
    
    def _setup_components(self):
        """Initialize all GUI components"""
        self.background_setup = BackgroundSetup(self.master)
        self.panel_setup = PanelSetup(self.master, self.master.settings_manager, self.background_setup)
        self.content_setup = ContentSetup(self.master, self.master.settings_manager)
        self.settings_setup = SettingsTabSetup(self.master, self.master.settings_manager)
        self.state_manager = GUIStateManager(self.master)
        self.scraper_manager = ScraperManager(self.master, self.master.settings_manager)
        
        self._setup_callbacks()
    
    def _setup_callbacks(self):
        """Setup callback connections"""
        if hasattr(self.content_setup, 'on_website_selection'):
            self.content_setup.on_website_selection = self.on_selection_instantiate
    
    def setup(self):
        """Main setup method to create the entire GUI"""
        self.background_setup.setup_background()
        
        self.panel_setup.create_panels()
        
        self.content_setup.add_left_panel_content()
        self.content_setup.add_right_panel_content()
        
        self.settings_setup.setup_settings_tab(self.master.settings_tab)
        
        self.setup_info_tab(self.master.info_tab)
        self.setup_price_history_tab(self.master.price_history_changes_tab)
        
        
        print("GUI setup complete")
    
    def on_selection_instantiate(self, selected_website):
        """Handle website selection and scraper instantiation"""
        if hasattr(self.master, 'left_website_select'):
            self.master.left_website_select.set(selected_website)

        scraper = self.scraper_manager.instantiate_scraper(selected_website)

        if selected_website in self.master.selected_websites:
            self.master.update_gui({
                'type': 'status',
                'message': f"⚠️ {selected_website} is already selected"
            })
            return None
    
        if len(self.master.selected_websites) >= self.master.website_selection_limit:
            self.master.update_gui({
                'type': 'error',
                'message': f"❌ Worker limit reached! You can only select {self.master.website_selection_limit} website(s) at once (based on your CPU)."
            })
            return None
    
        if selected_website not in self.master.selected_websites:
            self.master.selected_websites.append(selected_website)
            print(f"Added {selected_website} to selected websites")
            self.master.scraper_list.append(scraper)
        
            if not self.master.scraper_container:
                self.master.scraper_container = ScraperContainer(self.master.scraper_list)
            else:
                self.master.scraper_container.scraper_list = self.master.scraper_list
        
            remaining = abs(self.master.website_selection_limit - len(self.master.selected_websites))
            self.master.update_gui({
                'type': 'status',
                'message': f"✅ {selected_website} selected ({len(self.master.selected_websites)}/{self.master.website_selection_limit}). {remaining} more website(s) can be selected."
            })
        return scraper

    def get_current_scraper(self):
        """Get the current active scraper"""
        return self.scraper_manager.get_current_scraper()
    
    def start_scraping(self):
        """Start the scraping process"""
        if not hasattr(self.master, 'current_scraper') or not self.master.current_scraper:
            self.master.update_gui("No scraper selected. Please select a website first.", level="error")
            return
        
        search_term = self.master.left_entry.get() if hasattr(self.master, 'left_entry') else ""
        
        if not search_term:
            self.master.update_gui("Please enter a search term", level="warning")
            return
        
        selected_part = self.master.left_part_select.get() if hasattr(self.master, 'left_part_select') else "GPU"
        
        if hasattr(self.master, 'status_label'):
            self.master.status_label.configure(text=f"Scraping {selected_part}...")

        if hasattr(self.master, '_start_scraping'):
            self.master._start_scraping()
        else:
            self.master.update_gui("Scraping functionality not implemented in main app", level="error")

    
    def setup_info_tab(self, tab):
        """Setup the info tab"""
        info_label = ctk.CTkLabel(tab, text="Application Information", 
                                  font=(self.master.preferred_font, 20, "bold"),
                                              fg_color=("#F5DBBD", "#1A1A1A"),
                                              padx=10, pady=10, corner_radius=10)
        info_label.pack(pady=20)
        
        info_text = ctk.CTkTextbox(tab, wrap="word", 
                                   font=(self.master.preferred_font, self.master.preferred_size),
                                               fg_color=("#F5DBBD", "#1A1A1A"),
            border_color=("#F5DBBD", "#1A1A1A"))
        
        info_text.pack(fill="both", expand=True, padx=20, pady=10)
        
        info_content = """
    PC Parts Web Scraper

    This application allows you to scrape PC parts prices from various online stores.

    Features:
    - Scrape prices from multiple websites
    - Compare prices across different currencies
    - Export results to Excel
    - Customizable settings

    Supported Websites:
    - Desktop.bg
    - Ardes.bg
    - Amazon.com
    - Amazon.co.uk
    - And many more...

    Instructions:
    1. Select the type of PC part you want to search for
    2. Choose the website to scrape
    3. Enter your search term
    4. Click the search button to start scraping
    5. View results in the console and exported Excel file

    Note: Some websites may have anti-bot protection that could affect scraping results.
    """
        info_text.insert("1.0", info_content)
        info_text.configure(state="disabled")
    
    def setup_price_history_tab(self, tab):
        """Setup the price history comparison tab"""
        info_label = ctk.CTkLabel(tab, text="Price History Comparison", 
                                  font=(self.master.preferred_font, 20, "bold"),
                                              fg_color=("#F5DBBD", "#1A1A1A"),
                                              padx=2, pady=2, corner_radius=10)
        info_label.pack(pady=20)
        
        self.master.price_comparison_panel = ctk.CTkFrame(
            tab, 
            width=500, 
            height=700,
            fg_color=("#F5DBBD", "#1A1A1A"),
            border_width=2,
        )
        self.master.price_comparison_panel.place(x=60, y=55, relwidth=0.9, relheight=0.9)
        
        self.left_part_select_comparison = ctk.CTkComboBox(
            self.master.price_comparison_panel,
            width=170,  
            height=40,
            fg_color=("#F5DBBD", "#1A1A1A"),
            values=self.part_options,
            corner_radius=20,  
            text_color=("black", "white"),  
            dropdown_fg_color=("#F5DBBD", "#1A1A1A"),  
            dropdown_text_color=("black", "white"),
            state='readonly',
            command=self.set_part_comparison,
            font=(self.master.preferred_font, self.master.preferred_size)
        )
        self.left_part_select_comparison.set("GPU")
        self.left_part_select_comparison.place(relx=0.02, rely=0.02)
        
        first_website_label = ctk.CTkLabel(
            self.master.price_comparison_panel,
            text='Choose first website to compare prices:',
            font=(self.master.preferred_font, 15, "bold")
        )
        first_website_label.place(relx=0.2, rely=0.03)
        
        self.first_website_select_comparison = ctk.CTkComboBox(
            self.master.price_comparison_panel,
            width=170,  
            height=40,
            fg_color=("#F5DBBD", "#1A1A1A"),
            values=self.website_options,
            corner_radius=20,
            border_color=[self.master.primary_color, self.master.secondary_color],
            text_color=("black", "white"),  
            dropdown_text_color=("black", "white"),
            state='readonly',
            command=self.set_first_website_for_comparison,
            font=(self.master.preferred_font, self.master.preferred_size)
        )
        self.first_website_select_comparison.set(self.master.first_website_for_comparison)
        self.first_website_select_comparison.place(relx=0.5, rely=0.02)
        
        self.second_website_select_comparison = ctk.CTkComboBox(
            self.master.price_comparison_panel,
            width=170,  
            height=40,
            fg_color=("#F5DBBD", "#1A1A1A"),
            values=self.website_options,
            corner_radius=20,
            border_color=[self.master.primary_color, self.master.secondary_color],
            text_color=("black", "white"),  
            dropdown_text_color=("black", "white"),
            state='readonly',
            command=self.set_second_website_for_comparison,
            font=(self.master.preferred_font, self.master.preferred_size)
        )
        self.second_website_select_comparison.set(self.master.second_website_for_comparison)
        self.second_website_select_comparison.place(relx=0.67, rely=0.02)
        
        self.begin_comparison_button = ctk.CTkButton(
            self.master.price_comparison_panel,
            width=40,
            height=40,
            corner_radius=20,
            font=(self.master.preferred_font, 15),
            text='Compare Data',
            command=self.master._make_historical_comparison
        )
        self.begin_comparison_button.place(relx=0.85, rely=0.02)
    
    def set_part_comparison(self, selected_part):
        """Set part for comparison"""
        print(f"Setting comparison part to: {selected_part}")
        self.master.part_to_compare_historically = selected_part
    
    def set_first_website_for_comparison(self, website):
        """Set first website for comparison"""
        print(f"Setting first comparison website to: {website}")
        self.master.first_website_for_comparison = website
        self.master.settings_manager.set('first_website_for_comparison', website)
    
    def set_second_website_for_comparison(self, website):
        """Set second website for comparison"""
        print(f"Setting second comparison website to: {website}")
        self.master.second_website_for_comparison = website
        self.master.settings_manager.set('second_website_for_comparison', website)

    def refresh_gui(self):
        """Completely refresh the GUI while preserving user input"""
        print("Refreshing GUI with updated settings...")
        
        current_state = self.state_manager.capture_current_state()

        self._destroy_all_widgets()
        
        self._load_settings()

        self.setup()
        
        self.state_manager.restore_state(current_state)
        
        if hasattr(self.master, 'apply_custom_colors'):
            self.master.apply_custom_colors()
        
        print("GUI refresh complete")

    def _destroy_all_widgets(self):
        """Destroy all widgets in the main window"""
        for widget in self.master.winfo_children():
            try:
                widget.destroy()
            except:
                pass
        
        widget_attrs = [
            'scraper_tab', 'settings_tab', 'info_tab', 'price_history_changes_tab',
            'left_panel', 'right_panel', 'left_entry', 'left_part_select', 
            'left_website_select', 'left_select_folder_button', 'progress_bar',
            'status_label', 'left_scrape_button', 'right_console', 'options_menu',
            'price_comparison_panel', 'current_scraper', 'left_part_select_comparison',
            'first_website_select_comparison', 'second_website_select_comparison',
            'begin_comparison_button'
        ]
        
        for attr in widget_attrs:
            if hasattr(self.master, attr):
                delattr(self.master, attr)
    
    def change_theme(self, theme):
        """Change application theme"""
        self.master.preferred_theme = theme
        self.master.settings_manager.set_ui_setting('preferred_theme', theme)
        ctk.set_appearance_mode(theme.lower())
        print(f"Theme changed to: {theme}")
        self.refresh_gui()
    
    def pick_primary_color(self):
        """Pick primary color"""
        try:
            from tkinter import colorchooser
            color = colorchooser.askcolor(title="Choose primary color")[1]
            if color:
                self.master.primary_color = color
                self.master.settings_manager.set_ui_setting('primary_color', color)
                self.apply_custom_colors()
        except Exception as e:
            print(f"Error picking color: {e}")
    
    def pick_secondary_color(self):
        """Pick secondary color"""
        try:
            from tkinter import colorchooser
            color = colorchooser.askcolor(title="Choose secondary color")[1]
            if color:
                self.master.secondary_color = color
                self.master.settings_manager.set_ui_setting('secondary_color', color)
                self.apply_custom_colors()
        except Exception as e:
            print(f"Error picking color: {e}")
    
    def apply_custom_colors(self):
        """Apply custom colors to the theme"""
        try:
            self.master.settings_manager.update_theme()
            ctk.set_default_color_theme(self.master.settings_manager.get_theme_path())
            if hasattr(self.master, 'update_widget_colors'):
                self.master.update_widget_colors()
            print(f"Applied custom colors: Primary {self.master.primary_color}, Secondary {self.master.secondary_color}")
        except Exception as e:
            print(f"Error applying custom colors: {e}")
    
    def apply_preset_colors(self, primary, secondary):
        """Apply preset color combination"""
        self.master.primary_color = primary
        self.master.secondary_color = secondary
        self.master.settings_manager.set_ui_setting('primary_color', primary)
        self.master.settings_manager.set_ui_setting('secondary_color', secondary)
        self.apply_custom_colors()
    
    def create_custom_theme(self):
        """Create custom theme file"""
        config_dir = self.master.settings_manager.get_config_directory()
        theme_path = os.path.join(config_dir, "custom_theme.json")
        
        theme_data = {
            "CTk": {
                "fg_color": ["#DCE4EE", "#1B1B1B"],
                "top_fg_color": ["#DCE4EE", "#1B1B1B"],
                "text_color": ["#000000", "#FFFFFF"]
            },
            "CTkButton": {
                "corner_radius": 8,
                "border_width": 0,
                "fg_color": [self.master.primary_color, self.master.primary_color],
                "hover_color": [self.master.secondary_color, self.master.secondary_color],
                "text_color": ["#FFFFFF", "#FFFFFF"],
                "border_color": ["#3E454A", "#949A9F"]
            },
            "CTkFrame": {
                "corner_radius": 8,
                "border_width": 1,
                "fg_color": ["#F0F0F0", "#2B2B2B"],
                "border_color": [self.master.primary_color, self.master.primary_color]
            },
            "CTkEntry": {
                "corner_radius": 6,
                "border_width": 1,
                "fg_color": ["#FFFFFF", "#1E1E1E"],
                "border_color": [self.master.primary_color, self.master.primary_color],
                "text_color": ["#000000", "#FFFFFF"]
            },
            "CTkProgressBar": {
                "corner_radius": 4,
                "border_width": 0,
                "fg_color": ["#E0E0E0", "#404040"],
                "progress_color": [self.master.secondary_color, self.master.secondary_color]
            },
            "CTkComboBox": {
                "button_color": self.master.primary_color,
                "button_hover_color": self.master.secondary_color,
                "fg_color": ("#FFFFFF", "#1A1A1A"),
                "text_color": ("black", "white"),
                "dropdown_fg_color": ("#FFFFFF", "#1A1A1A"),
                "dropdown_hover_color": (self.master.primary_color, self.master.secondary_color),
                "dropdown_text_color": ("black", "white")
            },
        }
        
        try:
            with open(theme_path, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=4, ensure_ascii=False)
            print(f"Custom theme saved to {theme_path}")
            return theme_path
        except Exception as e:
            print(f"Error saving custom theme: {e}")
            return None
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.master.settings_manager.settings = self.master.settings_manager.default_settings.copy()
        self.master.settings_manager.save_settings()
        
        self.master.settings_manager.create_default_theme()
        ctk.set_default_color_theme(self.master.settings_manager.get_theme_path())
        
        self._load_settings()
        self.refresh_gui()
        
        print("Reset all settings to defaults")
    
    def cleanup(self):
        """Clean up all resources"""
        self.scraper_manager.cleanup()