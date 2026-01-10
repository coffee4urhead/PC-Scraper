from PIL import Image, ImageFilter
from customtkinter import CTk as ctk
import customtkinter as ctk
import os 
import sys
import json
from settings_manager import SettingsManager

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

def resource_path(relative_path): 
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else: base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

class SetupGUI():
    def __init__(self, master=None):
        self.master = master
        if not hasattr(self.master, 'settings_manager'):
            self.master.settings_manager = SettingsManager()

        theme_path = self.master.settings_manager.get_theme_path()
        ctk.set_default_color_theme(theme_path) 
        ctk.set_appearance_mode(self.master.settings_manager.get_ui_setting('preferred_theme', 'System').lower())

        self.master.tab_backgrounds = [] 
        self.master.preferred_currency = self.master.settings_manager.get('preferred_currency', 'BGN')
        self.master.price_format = self.master.settings_manager.get('price_format', '0.00')
        self.master.currency_symbol = "лв"
        self.master.preferred_language = self.master.settings_manager.get_ui_setting('preferred_language', 'en-US')
        self.master.preferred_size = int(self.master.settings_manager.get_ui_setting('preferred_size', 16))
        self.master.preferred_browser = self.master.settings_manager.get('preferred_browser', 'Chrome')
        self.master.preferred_theme = self.master.settings_manager.get_ui_setting('preferred_theme', 'System')
        self.master.preferred_font = self.master.settings_manager.get_ui_setting('preferred_font', 'Verdana')
        self.master.save_folder = self.master.settings_manager.get_ui_setting('save_folder', os.path.join(os.path.expanduser("~"), "Desktop"))
        self.master.primary_color = self.master.settings_manager.get_ui_setting('primary_color', '#3B8ED0')
        self.master.secondary_color = self.master.settings_manager.get_ui_setting('secondary_color', '#1F6AA5')
        self.master.selected_pc_part = "GPU"
        self.master.first_website_for_comparison = self.master.settings_manager.get('first_website_for_comparison', 'Ardes,bg')
        self.master.second_website_for_comparison = self.master.settings_manager.get('second_website_for_comparison', 'Desktop.bg')
        self.master.part_to_compare_historically = 'GPU'

    def setup_background(self):
        bg_image_path = resource_path("images/nebula-star.png")
        pil_image = Image.open(bg_image_path).convert("RGB")
        
        pil_image = pil_image.resize((1200, 700))
        blurred = pil_image.filter(ImageFilter.GaussianBlur(radius=5))

        overlay = Image.new("RGB", blurred.size, (255, 255, 255))
        self.blended_bg = Image.blend(blurred, overlay, alpha=0.2)
        
        self.master.bg_image = ctk.CTkImage(light_image=self.blended_bg, size=(1200, 700))

    def create_panels(self):
        tabview = ctk.CTkTabview(self.master)
        tabview.pack(fill="both", expand=True)
        
        self.master.scraper_tab = tabview.add("Scraper")
        self.master.settings_tab = tabview.add("Settings")
        self.master.info_tab = tabview.add("Info")
        self.master.price_history_changes_tab = tabview.add("Price History changes")

        self.apply_background_to_tab(self.master.scraper_tab)
        self.apply_background_to_tab(self.master.settings_tab)
        self.apply_background_to_tab(self.master.info_tab)
        self.apply_background_to_tab(self.master.price_history_changes_tab)

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

        self.add_panel_content()

        self.setup_settings_tab(self.master.settings_tab)
        self.setup_info_tab(self.master.info_tab)
        self.setup_price_history_tab(self.master.price_history_changes_tab)

    def add_panel_content(self):
        left_title = ctk.CTkLabel(
            self.master.left_panel,
            text="PC Parts Web Scraper",
            text_color="white",
            font=(self.master.preferred_font, self.master.preferred_size, "bold"),
            fg_color="transparent"
        )
        left_title.place(relx=0.05, rely=0.02)

        self.master.left_entry = ctk.CTkEntry(
            self.master.left_panel, 
            width=300, 
            height=40, 
            corner_radius=20, 
            text_color=("black", "white"),
            placeholder_text='Enter your desired part here ...',
            placeholder_text_color=("#666666", "#888888"),
            font=(self.master.preferred_font, self.master.preferred_size)
        )
        self.master.left_entry.place(relx=0.05, rely=0.1) 

        self.options = ['Ardes.bg', 'AllStore.bg', 'Amazon.co.uk', 'Hits.bg', 'Tova.bg', 'Ezona.bg', 'GtComputers.bg', 'Thx.bg', 'Senetic.bg', 'TehnikStore.bg', 'Pro.bg', 'TechnoMall.bg', 'PcTech.bg', 'CyberTrade.bg', 'Xtreme.bg', 'Optimal Computers', 'Plasico.bg', 'PIC.bg', 'jarcomputers.com', 'Desktop.bg', 'Amazon.com', 'Amazon.de']
        self.part_options = ["Motherboard", 'PSU', 'RAM', 'GPU', 'Case', 'Fans', 'CPU', 'AIO', 'Air Coolers', 'Extension Cables', 'HDD', 'SATA SSD', 'NVME SSD']

        self.master.left_part_select = ctk.CTkComboBox(
            self.master.left_panel,
            width=170,  
            height=40,
            fg_color=("#FFFFFF", "#1A1A1A"),
            values=self.part_options,
            corner_radius=20,  
            text_color=("black", "white"),  
            dropdown_fg_color=("#FFFFFF", "#1A1A1A"),  
            dropdown_text_color=("black", "white"),
            state='readonly',
            command=self.master.on_selection,
            font=(self.master.preferred_font, self.master.preferred_size)
        )
        self.master.left_part_select.set("GPU")
        self.master.left_part_select.place(relx=0.6, rely=0.02)
        
        self.master.left_website_select = ctk.CTkComboBox(
            self.master.left_panel,
            width=170,  
            height=40,
            fg_color=("#FFFFFF", "#1A1A1A"),
            values=self.options,
            corner_radius=20,
            border_color=[self.master.primary_color, self.master.secondary_color],
            text_color=("black", "white"),  
            dropdown_text_color=("black", "white"),
            state='readonly',
            command=self.on_selection_instantiate,
            font=(self.master.preferred_font, self.master.preferred_size)
        )
        self.master.left_website_select.set('Desktop.bg')
        self.master.left_website_select.place(relx=0.6, rely=0.1)

        bg_image_path = resource_path("images/Uriy1966-Steel-System-Library-Mac.64.png")
        pil_image = Image.open(bg_image_path)

        ctk_image = ctk.CTkImage(
            light_image=pil_image,
            dark_image=pil_image,
            size=(30, 30),
        )

        self.master.left_select_folder_button = ctk.CTkButton(
            self.master.left_panel,
            width=40,
            height=40,
            corner_radius=10,
            fg_color=("#FFFFFF", "#454345"),
            hover_color=("#CBC7C7", "#2E2C2E"),
            image=ctk_image,
            command=self.master.ask_save_dir,
            text=''
        )
        self.master.left_select_folder_button.place(relx=0.9, rely=0.1)

        self.master.progress_bar = ctk.CTkProgressBar(
            self.master.left_panel,
            width=1000,
            height=40,
            corner_radius=20,
        )
        self.master.progress_bar.place(relx=0.05, rely=0.2, relwidth=0.9)

        self.master.status_label = ctk.CTkLabel(
            self.master.left_panel,
            text="Ready to scrape...",
            text_color=("black", "white"),
            font=(self.master.preferred_font, self.master.preferred_size),
            fg_color="transparent"
        )
        self.master.status_label.place(relx=0.05, rely=0.25)

        search_icon_path = resource_path("images/search.png")
        search_pil_image = Image.open(search_icon_path)

        search_ctk_image = ctk.CTkImage(
            light_image=search_pil_image,
            dark_image=search_pil_image,
            size=(30, 30),
        )
        self.master.left_scrape_button = ctk.CTkButton(
            self.master.left_panel,
            width=40,
            height=40,
            corner_radius=20,
            font=(self.master.preferred_font, 30),
            image=search_ctk_image,
            text='',
            command=self.master._start_scraping
        )
        self.master.left_scrape_button.place(relx=0.48, rely=0.1)

        left_frame_label_container = ctk.CTkFrame(
            self.master.left_panel, 
            width=600, 
            height=400,
            fg_color=("#DBD8D8", "#232323"),
            border_width=2,
            border_color=("#FFFFFF", "#1A1A1A"),
            corner_radius=30
        )
        left_frame_label_container.place(relx=0.09, rely=0.3)

        left_label_container = ctk.CTkFrame(
            left_frame_label_container,
            fg_color="transparent"
        )
        left_label_container.pack(fill='both', expand=True, padx=100, pady=100)

        left_label_description = ctk.CTkLabel(
            left_label_container,
            text='Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industrys standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.',
            anchor='w',
            font=(self.master.preferred_font, self.master.preferred_size),
            justify='left',
            wraplength=450,  
        )
        left_label_description.pack(fill='both', expand=True, padx=10, pady=10)

        options_icon_path = resource_path("images/gears.png")
        gearwheel_image = Image.open(options_icon_path)
        gearwheel_image_ctk = ctk.CTkImage(light_image=gearwheel_image, dark_image=gearwheel_image, size=(40, 40))
        self.master.options_menu = ctk.CTkButton(
            self.master.left_panel,
            width=40,
            height=40,
            fg_color=("#E79CEE", "#C251CC"),
            hover_color=("#E7A2EE", "#CF55DA"),
            text='',
            image=gearwheel_image_ctk,
            command=self.master.get_scraper_windows_options
        )
        self.master.options_menu.place(relx=0.9, rely=0.9)

        self.audio_icon_path_on = resource_path("images/sound.png")
        self.audio_icon_path_off = resource_path("images/no-sound.png")
        
        try:
            audio_image_off = Image.open(self.audio_icon_path_off)
            self.audio_image_ctk_off = ctk.CTkImage(
                light_image=audio_image_off, 
                dark_image=audio_image_off, 
                size=(40, 40)
            )
            
            audio_image_on = Image.open(self.audio_icon_path_on)
            self.audio_image_ctk_on = ctk.CTkImage(
                light_image=audio_image_on, 
                dark_image=audio_image_on, 
                size=(40, 40)
            )
        except Exception as e:
            print(f"Error loading audio icons: {e}")
            self.audio_image_ctk_off = None
            self.audio_image_ctk_on = None

        self.mute_audio_btn = ctk.CTkButton(
            self.master.left_panel,
            width=40,
            height=40,
            fg_color=("#E79CEE", "#C251CC"),
            hover_color=("#E7A2EE", "#CF55DA"),
            text='' if self.audio_image_ctk_off else 'Music',
            image=self.audio_image_ctk_off, 
        )
        self.mute_audio_btn.place(relx=0.8, rely=0.9)

        right_title = ctk.CTkLabel(
            self.master.right_panel,
            text="Console", 
            text_color="white",
            font=(self.master.preferred_font, 20, "bold"),
            fg_color="transparent"
        )
        right_title.place(relx=0.05, rely=0.02)

        self.master.right_console = ctk.CTkTextbox(
            self.master.right_panel,
            width=350,
            height=500,
            fg_color=("#FFFFFF", "#000000"),
            text_color='green',
            wrap='word',
            font=(self.master.preferred_font, self.master.preferred_size)
        )
        self.master.right_console.place(relx=0.05, rely=0.1)

    def on_selection_instantiate(self, selected_value):
        self.selected_website = selected_value
    
        print(f"DEBUG: Initializing scraper for {self.selected_website}")
    
        try:
            if self.selected_website == "Amazon.com":
                self.scraper = AmazonComScraper('USD', self.master.update_gui)  
            elif self.selected_website == "Ardes.bg":
                self.scraper = ArdesScraper('BGN', self.master.update_gui)   
            elif self.selected_website == 'jarcomputers.com':
                self.scraper = JarComputersScraper('BGN', self.master.update_gui)  
            elif self.selected_website == "Desktop.bg":
                self.scraper = DesktopScraper('BGN', self.master.update_gui)
            elif self.selected_website == "Plasico.bg":
                self.scraper = PlasicoScraper('BGN', self.master.update_gui)
            elif self.selected_website == "PIC.bg":
                self.scraper = PICBgScraper('BGN', self.master.update_gui)
            elif self.selected_website == "Optimal Computers":
                self.scraper = OptimalComputersScraper('BGN', self.master.update_gui)
            elif self.selected_website == "Xtreme.bg":
                self.scraper = XtremeScraper('BGN', self.master.update_gui)
            elif self.selected_website == "CyberTrade.bg":
                self.scraper = CyberTradeScraper('BGN', self.master.update_gui)
            elif self.selected_website == "PcTech.bg":
                self.scraper = PcTechBgScraper('BGN', self.master.update_gui)
            elif self.selected_website == "Pro.bg":
                self.scraper = ProBgScraper('BGN', self.master.update_gui)
            elif self.selected_website == "TechnoMall.bg":
                self.scraper = TechnoMallScraper('BGN', self.master.update_gui)
            elif self.selected_website == "TehnikStore.bg":
                self.scraper = TehnikStoreScraper('BGN', self.master.update_gui)
            elif self.selected_website == "AllStore.bg":
                self.scraper = AllStoreScraper('BGN', self.master.update_gui)
            elif self.selected_website == "Senetic.bg":
                self.scraper = SeneticScraper('BGN', self.master.update_gui)
            elif self.selected_website == "Thx.bg":
                self.scraper = ThxScraper('BGN', self.master.update_gui)
            elif self.selected_website == "GtComputers.bg":
                self.scraper = GtComputersScraper('BGN', self.master.update_gui)
            elif self.selected_website == "Ezona.bg":
                self.scraper = EZonaScraper('BGN', self.master.update_gui)
            elif self.selected_website == "Tova.bg":
                self.scraper = TovaBGScraper('BGN', self.master.update_gui)
            elif self.selected_website == "Hits.bg":
                self.scraper = HitsBGScraper('BGN', self.master.update_gui)
            elif self.selected_website == "Amazon.co.uk":
                self.scraper = AmazonCoUkScraper('GBP', self.master.update_gui)
            elif self.selected_website == "Amazon.de":
                self.scraper = AmazonDeScraper('EUR', self.master.update_gui)

            self.master.settings_manager.apply_to_scraper(self.scraper)
            print(f"DEBUG: Scraper created successfully for {self.selected_website}")
           
        except Exception as e:
            print(f"DEBUG: Scraper initialization failed: {e}")
    
    def refresh_gui(self):
        """Completely refresh the GUI while preserving user input"""
        print("Refreshing GUI with updated settings...")
    
        # Store current user input and selections
        current_state = self._capture_current_state()
    
        # Clear all existing widgets
        self._destroy_all_widgets()
    
        # Re-initialize settings from settings manager (in case they changed)
        self._reload_settings()
    
        # Recreate the entire GUI
        self.setup_background()
        self.create_panels()
    
        # Restore user input and selections
        self._restore_state(current_state)
    
        # Apply any custom colors
        if hasattr(self.master, 'apply_custom_colors'):
            self.master.apply_custom_colors()

    def _capture_current_state(self):
        """Capture all current user inputs and selections"""
        state = {}
    
        # Capture text inputs
        if hasattr(self.master, 'left_entry'):
            state['search_text'] = self.master.left_entry.get()
    
        # Capture dropdown selections
        if hasattr(self.master, 'left_part_select'):
            state['selected_part'] = self.master.left_part_select.get()
    
        if hasattr(self.master, 'left_website_select'):
            state['selected_website'] = self.master.left_website_select.get()
    
        # Capture settings tab selections
        if hasattr(self, 'font_family_select'):
            state['font_family'] = self.font_family_select.get()
    
        if hasattr(self, 'font_size_select'):
            state['font_size'] = self.font_size_select.get()
    
        if hasattr(self, 'language_select'):
            state['language'] = self.language_select.get()
    
        # Capture console content
        if hasattr(self.master, 'right_console'):
            state['console_text'] = self.master.right_console.get("1.0", "end-1c")
    
        return state

    def _destroy_all_widgets(self):
        """Destroy all widgets in the main window"""
        # Destroy all children of the main window
        for widget in self.master.winfo_children():
            try:
                widget.destroy()
            except:
                pass
    
        # Clear any stored widget references
        if hasattr(self, 'tab_backgrounds'):
            self.tab_backgrounds.clear()
    
        # Clear master's widget references
        widget_attrs = [
            'scraper_tab', 'settings_tab', 'info_tab', 'price_history_changes_tab',
            'left_panel', 'right_panel', 'left_entry', 'left_part_select', 
            'left_website_select', 'left_select_folder_button', 'progress_bar',
            'status_label', 'left_scrape_button', 'right_console', 'options_menu'
        ]
    
        for attr in widget_attrs:
            if hasattr(self.master, attr):
                delattr(self.master, attr)

    def _reload_settings(self):
        """Reload settings from settings manager"""
        # Reload font settings
        self.master.preferred_font = self.master.settings_manager.get_ui_setting('preferred_font', 'Verdana')
        self.master.preferred_size = int(self.master.settings_manager.get_ui_setting('preferred_size', 15))
        self.master.preferred_language = self.master.settings_manager.get_ui_setting('preferred_language', 'en-US')
        self.master.preferred_theme = self.master.settings_manager.get_ui_setting('preferred_theme', 'System')
    
        # Reload color settings
        self.master.primary_color = self.master.settings_manager.get_ui_setting('primary_color', '#3B8ED0')
        self.master.secondary_color = self.master.settings_manager.get_ui_setting('secondary_color', '#1F6AA5')
    
        # Apply theme
        ctk.set_appearance_mode(self.master.preferred_theme.lower())

    def _restore_state(self, state):
        """Restore user inputs and selections"""
        # Restore text input
        if 'search_text' in state and hasattr(self.master, 'left_entry'):
            self.master.left_entry.insert(0, state['search_text'])
    
        # Restore dropdown selections
        if 'selected_part' in state and hasattr(self.master, 'left_part_select'):
            self.master.left_part_select.set(state['selected_part'])
    
        if 'selected_website' in state and hasattr(self.master, 'left_website_select'):
            self.master.left_website_select.set(state['selected_website'])
        
            # Also update the scraper for the selected website
            if hasattr(self, 'on_selection_instantiate'):
                self.on_selection_instantiate(state['selected_website'])
    
        # Restore settings tab selections
        if 'font_family' in state and hasattr(self, 'font_family_select'):
            self.font_family_select.set(state['font_family'])
    
        if 'font_size' in state and hasattr(self, 'font_size_select'):
            self.font_size_select.set(state['font_size'])
    
        if 'language' in state and hasattr(self, 'language_select'):
            self.language_select.set(state['language'])
    
        # Restore console content
        if 'console_text' in state and hasattr(self.master, 'right_console'):
            self.master.right_console.insert("1.0", state['console_text'])

    def apply_background_to_tab(self, tab):
        bg_label = ctk.CTkLabel(tab, image=self.master.bg_image, text="")
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        if not hasattr(self, 'tab_backgrounds'):
            self.tab_backgrounds = []
        self.master.tab_backgrounds.append(bg_label)
    
    def update_font_family(self, selected_font):
        """Update font family setting"""
        print(f"Updating font family to: {selected_font}")
        self.master.preferred_font = selected_font
        self.master.settings_manager.set_ui_setting('preferred_font', selected_font)
        self.refresh_gui() 

    def update_font_size(self, selected_size):
        """Update font size setting"""
        print(f"Updating font size to: {selected_size}")
        self.master.preferred_size = int(selected_size)
        self.master.settings_manager.set_ui_setting('preferred_size', selected_size)
        self.refresh_gui()

    def update_language(self, selected_language):
        """Update language setting"""
        print(f"Updating language to: {selected_language}")
        self.master.preferred_language = selected_language
        self.master.settings_manager.set_ui_setting('preferred_language', selected_language)
        self.refresh_gui()

    def set_part_comparison(self, selected_part):
        """Set part for comparison"""
        print(f"Setting comparison part to: {selected_part}")
        self.master.part_to_compare_historically = selected_part

    def set_first_website_for_comparison(self, website):
        """Set first website for comparison"""
        print(f"Setting first comparison website to: {website}")
        self.master.first_website_for_comparison = website

    def set_second_website_for_comparison(self, website):
        """Set second website for comparison"""
        print(f"Setting second comparison website to: {website}")
        self.master.second_website_for_comparison = website

    def setup_ui_colors_customization(self):
        title_label = ctk.CTkLabel(
            self.customize_ui_colors_dialog,
            text="UI Colors & Theme",
            text_color=("black", "white"),
            font=(self.master.preferred_font, 22, "bold"),
            fg_color="transparent"
        )
        title_label.place(relx=0.05, rely=0.05)
    
        separator = ctk.CTkFrame(
            self.customize_ui_colors_dialog,
            height=2,
            fg_color=("#E0E0E0", "#404040")
        )
        separator.place(relx=0.05, rely=0.12, relwidth=0.9)
    
        theme_section_label = ctk.CTkLabel(
            self.customize_ui_colors_dialog,
            text="Theme Selection",
            text_color=("black", "white"),
            font=(self.master.preferred_font, 16, "bold"),
            fg_color="transparent"
        )
        theme_section_label.place(relx=0.05, rely=0.15)
    
        theme_button_frame = ctk.CTkFrame(
            self.customize_ui_colors_dialog,
            fg_color="transparent",
            height=50
        )
        theme_button_frame.place(relx=0.05, rely=0.22, relwidth=0.9)
    
        self.light_theme_btn = ctk.CTkButton(
            theme_button_frame,
            text="🌞 Light",
            font=(self.master.preferred_font, 14),
            fg_color=("#F0F0F0", "#D0D0D0"),
            text_color="black",
            hover_color=("#E0E0E0", "#C0C0C0"),
            border_width=2,
            border_color=("#3B8ED0", "#1F6AA5"),
            command=lambda: self.change_theme("Light")
        )
        self.light_theme_btn.pack(side="left", padx=(0, 10))
    
        self.dark_theme_btn = ctk.CTkButton(
            theme_button_frame,
            text="🌙 Dark", 
            font=(self.master.preferred_font, 14),
            fg_color=("#2B2B2B", "#1A1A1A"),
            text_color="white",
            hover_color=("#3B3B3B", "#2A2A2A"),
            border_width=2,
            border_color=("#3B8ED0", "#1F6AA5"),
            command=lambda: self.change_theme("Dark")
        )
        self.dark_theme_btn.pack(side="left", padx=(0, 10))
    
        self.system_theme_btn = ctk.CTkButton(
            theme_button_frame,
            text="💻 System",
            font=(self.master.preferred_font, 14),
            fg_color=("#3B8ED0", "#1F6AA5"),
            text_color="white", 
            hover_color=("#357ABD", "#1A5A8A"),
            border_width=2,
            border_color=("#3B8ED0", "#1F6AA5"),
            command=lambda: self.change_theme("System")
        )
        self.system_theme_btn.pack(side="left")
    
        colors_separator = ctk.CTkFrame(
            self.customize_ui_colors_dialog,
            height=2,
            fg_color=("#E0E0E0", "#404040")
        )
        colors_separator.place(relx=0.05, rely=0.35, relwidth=0.9)
    
        colors_section_label = ctk.CTkLabel(
            self.customize_ui_colors_dialog,
            text="Custom Colors",
            text_color=("black", "white"),
            font=(self.master.preferred_font, self.master.preferred_size, "bold"),
            fg_color="transparent"
        )
        colors_section_label.place(relx=0.05, rely=0.4)
    
        color_picker_frame = ctk.CTkFrame(
            self.customize_ui_colors_dialog,
            fg_color="transparent",
            height=120
        )
        color_picker_frame.place(relx=0.05, rely=0.47, relwidth=0.9)
    
        primary_color_label = ctk.CTkLabel(
            color_picker_frame,
            text="Primary Color:",
            text_color=("black", "white"),
            font=(self.master.preferred_font, self.master.preferred_size),
            fg_color="transparent"
        )
        primary_color_label.grid(row=0, column=0, sticky="w", padx=(0, 20), pady=(0, 10))
    
        self.primary_color_display = ctk.CTkFrame(
            color_picker_frame,
            width=40,
            height=40,
            fg_color="#3B8ED0",
            corner_radius=8,
            border_width=2,
            border_color=("white", "black")
        )
        self.primary_color_display.grid(row=0, column=1, padx=(0, 20), pady=(0, 10))
    
        self.primary_color_btn = ctk.CTkButton(
            color_picker_frame,
            text="Pick Primary",
            font=(self.master.preferred_font, self.master.preferred_size),
            width=100,
            height=32,
            fg_color=("#3B8ED0", "#1F6AA5"),
            command=self.pick_primary_color,
        )
        self.primary_color_btn.grid(row=0, column=2, pady=(0, 10))
    
        secondary_color_label = ctk.CTkLabel(
            color_picker_frame,
            text="Secondary Color:",
            height=32,
            text_color=("black", "white"), 
            font=(self.master.preferred_font, 14),
            fg_color="transparent"
        )
        secondary_color_label.grid(row=1, column=0, sticky="w", padx=(0, 20), pady=(10, 0))
    
        self.secondary_color_display = ctk.CTkFrame(
            color_picker_frame,
            width=40,
            height=40,
            fg_color="#1F6AA5",
            corner_radius=8,
            border_width=2,
            border_color=("white", "black")
        )
        self.secondary_color_display.grid(row=1, column=1, padx=(0, 20), pady=(10, 0))
    
        self.secondary_color_btn = ctk.CTkButton(
            color_picker_frame,
            text="Pick Secondary", 
            font=(self.master.preferred_font, self.master.preferred_size),
            width=100,
            fg_color=("#3B8ED0", "#1F6AA5"),
            command=self.pick_secondary_color
        )
        self.secondary_color_btn.grid(row=1, column=2, pady=(10, 0))
    
        preset_colors_label = ctk.CTkLabel(
            color_picker_frame,
            text="Quick Presets:",
            text_color=("black", "white"),
            font=(self.master.preferred_font, self.master.preferred_size),
            fg_color="transparent"
        )
        preset_colors_label.grid(row=2, column=0, sticky="w", padx=(0, 20), pady=(15, 0))
    
        preset_colors_frame = ctk.CTkFrame(
            color_picker_frame,
            fg_color="transparent",
            height=30
        )
        preset_colors_frame.grid(row=2, column=1, columnspan=2, sticky="w", pady=(15, 0))
    
        preset_colors = [
            ("#3B8ED0", "#1F6AA5"),  # Blue
            ("#2E8B57", "#228B22"),  # Green  
            ("#FF6B6B", "#FF4757"),  # Red
            ("#FFA500", "#FF8C00"),  # Orange
            ("#9370DB", "#8A2BE2"),  # Purple
            ("#20B2AA", "#008B8B")   # Teal
        ]
    
        for i, (primary, secondary) in enumerate(preset_colors):
            preset_btn = ctk.CTkButton(
                preset_colors_frame,
                text="",
                width=25,
                height=25,
                fg_color=primary,
                hover_color=secondary,
                command=lambda p=primary, s=secondary: self.apply_preset_colors(p, s)
            )
            preset_btn._is_preset_button = True
            preset_btn.pack(side="left", padx=(0, 5))
    
        self.primary_color = "#3B8ED0"
        self.secondary_color = "#1F6AA5"

        reset_button = ctk.CTkButton(
            self.customize_ui_colors_dialog,
            text="Reset to Defaults",
            font=(self.master.preferred_font, 14),
            fg_color=("#FF6B6B", "#FF4757"),
            hover_color=("#FF5252", "#FF3838"),
            text_color="white",
            height=40,
            command=self.reset_to_defaults
        )
        reset_button.place(relx=0.05, rely=0.92, relwidth=0.9)
    
    def reset_to_defaults(self):
        self.master.settings_manager.settings = self.master.settings_manager.default_settings.copy()
        self.master.settings_manager.save_settings()

        self.master.settings_manager.create_default_theme()
        ctk.set_default_color_theme(self.master.settings_manager.get_theme_path())

        self.primary_color_display.configure(fg_color=self.primary_color)
        self.secondary_color_display.configure(fg_color=self.secondary_color)
        ctk.set_appearance_mode(self.master.preferred_theme.lower())

        if hasattr(self, 'font_family_select'):
            self.font_family_select.set(self.master.preferred_font)
            self.update_font_family(self.master.preferred_font)
    
        if hasattr(self, 'font_size_select'):
            self.font_size_select.set(str(self.master.preferred_size))
            self.update_font_size(str(self.master.preferred_size))

        self.apply_custom_colors()
    
        print("Reset all settings to defaults")

    def change_theme(self, theme):
        self.preferred_theme = theme
        self.master.settings_manager.set_ui_setting('preferred_theme', theme)
        ctk.set_appearance_mode(theme.lower())
        print(f"Theme changed to: {theme}")

    def pick_primary_color(self):
        color = self.ask_color()
        if color:
            self.primary_color = color
            self.master.settings_manager.set_ui_setting('primary_color', color)
            self.primary_color_display.configure(fg_color=color)
            self.apply_custom_colors()

    def pick_secondary_color(self):
        color = self.ask_color()
        if color:
            self.secondary_color = color
            self.master.settings_manager.set_ui_setting('secondary_color', color)
            self.secondary_color_display.configure(fg_color=color)
            self.apply_custom_colors()

    def ask_color(self):
        try:
            from tkinter import colorchooser
            color = colorchooser.askcolor(title="Choose color")[1]
            return color
        except:
            print("Color chooser not available")
            return None

    def apply_preset_colors(self, primary, secondary):
        self.primary_color = primary
        self.secondary_color = secondary
        self.master.settings_manager.set_ui_setting('primary_color', primary)
        self.master.settings_manager.set_ui_setting('secondary_color', secondary)
        self.primary_color_display.configure(fg_color=primary)
        self.secondary_color_display.configure(fg_color=secondary)
        self.apply_custom_colors()

    def apply_custom_colors(self):
        try:
            self.master.settings_manager.update_theme()
            ctk.set_default_color_theme(self.master.settings_manager.get_theme_path())
            self.master.update_widget_colors()
            print(f"Applied custom colors: Primary {self.primary_color}, Secondary {self.secondary_color}")
        except Exception as e:
            print(f"Error applying custom colors: {e}")
        
    def create_custom_theme(self):
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
                "fg_color": [self.primary_color, self.primary_color],
                "hover_color": [self.secondary_color, self.secondary_color],
                "text_color": ["#FFFFFF", "#FFFFFF"],
                "border_color": ["#3E454A", "#949A9F"]
            },
            "CTkFrame": {
                "corner_radius": 8,
                "border_width": 1,
                "fg_color": ["#F0F0F0", "#2B2B2B"],
                "border_color": [self.primary_color, self.primary_color]
            },
            "CTkEntry": {
                "corner_radius": 6,
                "border_width": 1,
                "fg_color": ["#FFFFFF", "#1E1E1E"],
                "border_color": [self.primary_color, self.primary_color],
                "text_color": ["#000000", "#FFFFFF"]
            },
            "CTkProgressBar": {
                "corner_radius": 4,
                "border_width": 0,
                "fg_color": ["#E0E0E0", "#404040"],
                "progress_color": [self.secondary_color, self.secondary_color]
            },
            "CTkComboBox": {
                "button_color": self.primary_color,
                "button_hover_color": self.secondary_color,
                "fg_color": ("#FFFFFF", "#1A1A1A"),
                "text_color": ("black", "white"),
                "dropdown_fg_color": ("#FFFFFF", "#1A1A1A"),
                "dropdown_hover_color": (self.primary_color, self.secondary_color),
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

    def setup_settings_tab(self, tab):
        self.look_and_feel_panel = ctk.CTkFrame(
            tab, 
            width=400,
            height=700,
            fg_color="#1A1A1A",  
            border_width=2,
            border_color=("#FFFFFF", "#1A1A1A"),
        )
        self.look_and_feel_panel.place(x=770, y=35, relwidth=0.33, relheight=0.9)

        look_and_feel_label = ctk.CTkLabel(
            self.look_and_feel_panel,
            text="Look and Feel", 
            text_color="white",
            font=(self.master.preferred_font, 20, "bold"),
            fg_color="transparent"
        )
        look_and_feel_label.place(relx=0.35, rely=0.02)
        
        font_label = ctk.CTkLabel(
            self.look_and_feel_panel,
            text="Font settings", 
            text_color="white",
            font=(self.master.preferred_font, 20, "bold"),
            fg_color="transparent"
        )
        font_label.place(relx=0.1, rely=0.1)

        font_frame = ctk.CTkFrame(
            tab, 
            width=400, 
            height=700, 
            fg_color="#1A1A1A",
            border_width=2,
            corner_radius=12,
        )
        font_frame.place(x=790, y=130, relwidth=0.3, relheight=0.23)

        font_family = ctk.CTkLabel(
            font_frame,
            text="Font Family", 
            text_color="white",
            font=(self.master.preferred_font, 15, "bold"),
            fg_color="transparent"
        )
        font_family.place(relx=0.1, rely=0.1)
        
        font_family_options = [
            "Arial",
            "Helvetica", 
            "Times New Roman",
            "Courier New",
            "Verdana",
            "Georgia",
            "Tahoma",
            "Trebuchet MS",
            "Comic Sans MS",
            "Impact",
            "Lucida Console",
            "Lucida Sans Unicode",
            "Palatino Linotype",
            "Garamond",
            "Bookman Old Style",
            "Arial Black",
            "Symbol",
            "Wingdings",
            "MS Sans Serif",
            "MS Serif",
            "Segoe UI",
            "Calibri",
            "Cambria",
            "Candara",
            "Consolas",
            "Constantia",
            "Corbel",
            "Franklin Gothic Medium",
            "Geneva",
            "Courier",
            "Monaco",
            "Andale Mono",
            "Monospace",
            "Sans-serif",
            "Serif"
        ]

        self.font_family_select = ctk.CTkComboBox(
            font_frame,
            width=170,
            height=40,
            fg_color=("#FFFFFF", "#1A1A1A"),
            values=font_family_options,
            corner_radius=20,
            border_color=[self.master.primary_color, self.master.secondary_color],
            text_color=("black", "white"),
            button_color=("#3B8ED0", "#1F6AA5"),
            dropdown_fg_color=("#FFFFFF", "#1A1A1A"),
            dropdown_text_color=("black", "white"),
            state='readonly', command=self.update_font_family,
            font=(self.master.preferred_font, self.master.preferred_size)
        )
        self.font_family_select.set("Verdana")
        self.font_family_select.place(relx=0.4, rely=0.05)

        language_label = ctk.CTkLabel(
            font_frame,
            text="Language", 
            text_color="white",
            font=(self.master.preferred_font, 15, "bold"),
            fg_color="transparent"
        )
        language_label.place(relx=0.1, rely=0.4)

        languages = [
                "af-ZA",  # Afrikaans - South Africa
                "ar-SA",  # Arabic - Saudi Arabia
                "bg-BG",  # Bulgarian - Bulgaria
                "ca-ES",  # Catalan - Spain
                "cs-CZ",  # Czech - Czech Republic
                "da-DK",  # Danish - Denmark
                "de-DE",  # German - Germany
                "el-GR",  # Greek - Greece
                "en-US",  # English - United States
                "en-GB",  # English - United Kingdom
                "es-ES",  # Spanish - Spain
                "es-MX",  # Spanish - Mexico
                "et-EE",  # Estonian - Estonia
                "fi-FI",  # Finnish - Finland
                "fr-FR",  # French - France
                "he-IL",  # Hebrew - Israel
                "hi-IN",  # Hindi - India
                "hr-HR",  # Croatian - Croatia
                "hu-HU",  # Hungarian - Hungary
                "id-ID",  # Indonesian - Indonesia
                "it-IT",  # Italian - Italy
                "ja-JP",  # Japanese - Japan
                "ko-KR",  # Korean - South Korea
                "lt-LT",  # Lithuanian - Lithuania
                "lv-LV",  # Latvian - Latvia
                "nb-NO",  # Norwegian Bokmål - Norway
                "nl-NL",  # Dutch - Netherlands
                "pl-PL",  # Polish - Poland
                "pt-BR",  # Portuguese - Brazil
                "pt-PT",  # Portuguese - Portugal
                "ro-RO",  # Romanian - Romania
                "ru-RU",  # Russian - Russia
                "sk-SK",  # Slovak - Slovakia
                "sl-SI",  # Slovenian - Slovenia
                "sr-RS",  # Serbian - Serbia
                "sv-SE",  # Swedish - Sweden
                "th-TH",  # Thai - Thailand
                "tr-TR",  # Turkish - Turkey
                "uk-UA",  # Ukrainian - Ukraine
                "vi-VN",  # Vietnamese - Vietnam
                "zh-CN",  # Chinese (Simplified) - China
                "zh-TW",  # Chinese (Traditional) - Taiwan
        ]
        self.language_select = ctk.CTkComboBox(
            font_frame,
            width=170,  
            height=40,
            fg_color=("#FFFFFF", "#1A1A1A"),
            values=languages,
            corner_radius=20,
            border_color=[self.master.primary_color, self.master.secondary_color],
            text_color=("black", "white"), 
            button_color=("#3B8ED0", "#1F6AA5"),  
            dropdown_fg_color=("#FFFFFF", "#1A1A1A"),  
            dropdown_text_color=("black", "white"),
            state='readonly',
            command=self.update_language,
            font=(self.master.preferred_font, self.master.preferred_size)
        )
        self.language_select.set("en-US")
        self.language_select.place(relx=0.4, rely=0.35)
        
        font_size_label = ctk.CTkLabel(
            font_frame,
            text="Font Size", 
            text_color="white",
            font=(self.master.preferred_font, 15, "bold"),
            fg_color="transparent"
        )
        font_size_label.place(relx=0.1, rely=0.7)
        font_size_options = [str(i) for i in range(18)]
        
        self.font_size_select = ctk.CTkComboBox(
            font_frame,
            width=170,  
            height=40,
            fg_color=("#FFFFFF", "#1A1A1A"),
            values=font_size_options,
            corner_radius=20, 
            border_color=[self.master.primary_color, self.master.secondary_color],
            text_color=("black", "white"), 
            button_color=("#3B8ED0", "#1F6AA5"),  
            dropdown_fg_color=("#FFFFFF", "#1A1A1A"),  
            dropdown_text_color=("black", "white"),
            state='readonly',
            command=self.update_font_size,
            font=(self.master.preferred_font, self.master.preferred_size)
        )
        self.font_size_select.set("15")
        self.font_size_select.place(relx=0.4, rely=0.65)
    
        self.customize_ui_colors_dialog = ctk.CTkFrame(
            tab, 
            width=400,
            height=1000,
            fg_color=("#1A1A1A", "#2D2D2D"),  
            border_width=2,
            border_color=("#3A3A3A", "#4A4A4A"),
            corner_radius=15
        )
        self.customize_ui_colors_dialog.place(x=25, y=35, relwidth=0.6, relheight=0.9)
    
        self.setup_ui_colors_customization()
    
    def setup_info_tab(self, tab):
        info_label = ctk.CTkLabel(tab, text="Application Information", 
                            font=(self.master.preferred_font, 20, "bold"))
        info_label.pack(pady=20)
    
        info_text = ctk.CTkTextbox(tab, wrap="word", font=(self.master.preferred_font, self.master.preferred_size))
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
        info_label = ctk.CTkLabel(tab, text="Price History Comparison", 
                            font=(self.master.preferred_font, 20, "bold"))
        info_label.pack(pady=20)

        self.master.price_comparison_panel = ctk.CTkFrame(
            tab, 
            width=500, 
            height=700,
            fg_color=("#FFFFFF", "#1A1A1A"),
            border_width=2,
        )
        self.master.price_comparison_panel.place(x=60, y=55, relwidth=0.9, relheight=0.9)

        self.left_part_select_comparison = ctk.CTkComboBox(
            self.master.price_comparison_panel,
            width=170,  
            height=40,
            fg_color=("#FFFFFF", "#1A1A1A"),
            values=self.part_options,
            corner_radius=20,  
            text_color=("black", "white"),  
            dropdown_fg_color=("#FFFFFF", "#1A1A1A"),  
            dropdown_text_color=("black", "white"),
            state='readonly',
            command=self.set_part_comparison,
            font=(self.master.preferred_font, self.master.preferred_size)
        )
        self.left_part_select_comparison.set("GPU")
        self.left_part_select_comparison.place(relx=0.02, rely=0.02)

        first_website_value_label = ctk.CTkLabel(
            self.master.price_comparison_panel,
            width=10,
            text='Choose first websites to compare prices',
            font=(self.master.preferred_font, 15, "bold")
        )
        first_website_value_label.place(relx=0.2, rely=0.03)

        self.first_website_select_comparison = ctk.CTkComboBox(
            self.master.price_comparison_panel,
            width=170,  
            height=40,
            fg_color=("#FFFFFF", "#1A1A1A"),
            values=self.options,
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
            fg_color=("#FFFFFF", "#1A1A1A"),
            values=self.options,
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