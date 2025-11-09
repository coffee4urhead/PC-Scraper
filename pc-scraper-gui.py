import customtkinter as ctk
from PIL import Image, ImageFilter
from tkinter import filedialog
from dotenv import load_dotenv
import os
import json
import sys
import TableMaker as tm

from windows.scraper_options_window import ScraperOptionsWindow
from settings_manager import SettingsManager

from currency_converter import convert_currency

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

load_dotenv() 

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS  
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class GUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PC Scraper GUI")
        self.geometry("1200x700")
        ctk.set_default_color_theme('blue')
        self.settings_manager = SettingsManager()
        
        self.preferred_currency = self.settings_manager.get('preferred_currency', 'BGN')
        self.price_format = self.settings_manager.get('price_format', '0.00')
        self.currency_symbol = "лв"  
        self.preferred_language = self.settings_manager.get_ui_setting('preferred_language', 'en-US')
        self.preferred_size = self.settings_manager.get_ui_setting('preferred_size', 15)
        self.preferred_browser = self.settings_manager.get('preferred_browser', 'Chrome')
        self.preferred_theme = self.settings_manager.get_ui_setting('preferred_theme', 'System')
        self.preferred_font = self.settings_manager.get_ui_setting('preferred_font', 'Verdana')
        self.save_folder = self.settings_manager.get_ui_setting('save_folder', os.path.join(os.path.expanduser("~"), "Desktop"))
        self.primary_color = self.settings_manager.get_ui_setting('primary_color', '#3B8ED0')
        self.secondary_color = self.settings_manager.get_ui_setting('secondary_color', '#1F6AA5')
        self.selected_pc_part = "GPU"

        ctk.set_appearance_mode(self.preferred_theme.lower())
        
        try:
            theme_path = self.settings_manager.get_theme_path()
            if os.path.exists(theme_path):
                ctk.set_default_color_theme(theme_path)
                print("Custom theme applied successfully")
            else:
                ctk.set_default_color_theme("blue")
                print("Using default blue theme")
        except Exception as e:
            print(f"Error applying custom theme: {e}")
            ctk.set_default_color_theme("blue")

        self.selected_website = "Desktop.bg"
        self.scraper = DesktopScraper('BGN', self.update_gui)
        self.settings_manager.apply_to_scraper(self.scraper)

        self.all_products = []
        self.scraper_options = None
        
        self.setup_background()
        self.create_panels()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.after(100, self.apply_custom_colors)

    def setup_background(self):
        bg_image_path = resource_path("images/nebula-star.png")
        pil_image = Image.open(bg_image_path).convert("RGB")
        
        pil_image = pil_image.resize((1200, 700))
        blurred = pil_image.filter(ImageFilter.GaussianBlur(radius=5))

        overlay = Image.new("RGB", blurred.size, (255, 255, 255))
        self.blended_bg = Image.blend(blurred, overlay, alpha=0.2)
        
        self.bg_image = ctk.CTkImage(light_image=self.blended_bg, size=(1200, 700))

    def create_panels(self):
        tabview = ctk.CTkTabview(self)
        tabview.pack(fill="both", expand=True)
        
        self.scraper_tab = tabview.add("Scraper")
        self.settings_tab = tabview.add("Settings")
        self.info_tab = tabview.add("Info")

        self.apply_background_to_tab(self.scraper_tab)
        self.apply_background_to_tab(self.settings_tab)
        self.apply_background_to_tab(self.info_tab)

        self.left_panel = ctk.CTkFrame(
            self.scraper_tab, 
            width=500, 
            height=700,
            fg_color=("#FFFFFF", "#1A1A1A"),
            border_width=2,
            border_color=("#FFFFFF", "#1A1A1A"),
        )
        self.left_panel.place(x=30, y=35, relwidth=0.6, relheight=0.9)

        self.right_panel = ctk.CTkFrame(
            self.scraper_tab, 
            width=400, 
            height=700, 
            fg_color="#1A1A1A",  
            border_width=2,
            border_color=("#FFFFFF", "#1A1A1A"),
        )
        self.right_panel.place(x=770, y=35, relwidth=0.33, relheight=0.9)

        self.add_panel_content()

        self.setup_settings_tab(self.settings_tab)
        self.setup_info_tab(self.info_tab)

    def add_panel_content(self):
        left_title = ctk.CTkLabel(
            self.left_panel,
            text="PC Parts Web Scraper",
            text_color="white",
            font=(self.preferred_font, self.preferred_size, "bold"),
            fg_color="transparent"
        )
        left_title.place(relx=0.05, rely=0.02)

        self.left_entry = ctk.CTkEntry(
            self.left_panel, 
            width=300, 
            height=40, 
            corner_radius=20, 
            text_color=("black", "white"),
            fg_color=("#FFFFFF", "#1A1A1A"),
            placeholder_text='Enter your desired part here ...',
            placeholder_text_color=("#666666", "#888888"),
            font=(self.preferred_font, self.preferred_size)
        )
        self.left_entry.place(relx=0.05, rely=0.1) 
        
        options = ['Ardes.bg', 'AllStore.bg', 'Amazon.co.uk', 'Hits.bg', 'Tova.bg', 'Ezona.bg', 'GtComputers.bg', 'Thx.bg', 'Senetic.bg', 'TehnikStore.bg', 'Pro.bg', 'TechnoMall.bg', 'PcTech.bg', 'CyberTrade.bg', 'Xtreme.bg', 'Optimal Computers', 'Plasico.bg', 'PIC.bg', 'jarcomputers.com', 'Desktop.bg', 'Amazon.com', 'Amazon.de']
        part_options = ["Motherboard", 'PSU', 'RAM', 'GPU', 'Case', 'Fans', 'CPU', 'AIO', 'Air Coolers', 'Extension Cables', 'HDD', 'SATA SSD', 'NVME SSD']

        self.left_part_select = ctk.CTkComboBox(
            self.left_panel,
            width=170,  
            height=40,
            fg_color=("#FFFFFF", "#1A1A1A"),
            values=part_options,
            corner_radius=20,
            border_color=("#E599F0", "#592461"),  
            text_color=("black", "white"), 
            button_color=("#3B8ED0", "#1F6AA5"),  
            dropdown_fg_color=("#FFFFFF", "#1A1A1A"),  
            dropdown_text_color=("black", "white"),
            state='readonly',
            command=self.on_selection,
            font=(self.preferred_font, self.preferred_size)
        )
        self.left_part_select.set("GPU")
        self.left_part_select.place(relx=0.6, rely=0.02)
        
        self.left_website_select = ctk.CTkComboBox(
            self.left_panel,
            width=170,  
            height=40,
            fg_color=("#FFFFFF", "#1A1A1A"),
            values=options,
            corner_radius=20,
            border_color=("#E599F0", "#592461"),  
            text_color=("black", "white"), 
            button_color=("#3B8ED0", "#1F6AA5"),  
            dropdown_fg_color=("#FFFFFF", "#1A1A1A"),  
            dropdown_text_color=("black", "white"),
            state='readonly',
            command=self.on_selection_instantiate,
            font=(self.preferred_font, self.preferred_size)
        )
        self.left_website_select.set('Desktop.bg')
        self.left_website_select.place(relx=0.6, rely=0.1)
        
        bg_image_path = resource_path("images/Uriy1966-Steel-System-Library-Mac.64.png")
        pil_image = Image.open(bg_image_path)

        ctk_image = ctk.CTkImage(
            light_image=pil_image,
            dark_image=pil_image,
            size=(30, 30),
        )

        self.left_select_folder_button = ctk.CTkButton(
            self.left_panel,
            width=40,
            height=40,
            corner_radius=10,
            fg_color=("#FFFFFF", "#454345"),
            hover_color=("#CBC7C7", "#2E2C2E"),
            image=ctk_image,
            command=self.ask_save_dir,
            text=''
        )
        self.left_select_folder_button.place(relx=0.9, rely=0.1)

        self.progress_bar = ctk.CTkProgressBar(
            self.left_panel,
            width=1000,
            height=40,
            corner_radius=20,
            fg_color=("#FFFFFF", "#2C2929"),
            progress_color=("#EBAEF5", "#E599F0")
        )
        self.progress_bar.place(relx=0.05, rely=0.2, relwidth=0.9)

        self.status_label = ctk.CTkLabel(
            self.left_panel,
            text="Ready to scrape...",
            text_color=("black", "white"),
            font=(self.preferred_font, self.preferred_size),
            fg_color="transparent"
        )
        self.status_label.place(relx=0.05, rely=0.25)

        search_icon_path = resource_path("images/search.png")
        search_pil_image = Image.open(search_icon_path)

        search_ctk_image = ctk.CTkImage(
            light_image=search_pil_image,
            dark_image=search_pil_image,
            size=(30, 30),
        )
        self.left_scrape_button = ctk.CTkButton(
            self.left_panel,
            width=40,
            height=40,
            corner_radius=20,
            font=(self.preferred_font, 30),
            fg_color=("#DFB6E5", "#E599F0"),
            border_color=("#E599F0", "#592461"),
            hover_color=("#C5A0CA", "#DE8DEB"),
            image=search_ctk_image,
            text='',
            command=self._start_scraping
        )
        self.left_scrape_button.place(relx=0.48, rely=0.1)

        left_frame_label_container = ctk.CTkFrame(
            self.left_panel, 
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
            font=(self.preferred_font, self.preferred_size),
            justify='left',
            wraplength=450,  
        )
        left_label_description.pack(fill='both', expand=True, padx=10, pady=10)

        options_icon_path = resource_path("images/gears.png")
        gearwheel_image = Image.open(options_icon_path)
        gearwheel_image_ctk = ctk.CTkImage(light_image=gearwheel_image, dark_image=gearwheel_image, size=(40, 40))
        self.options_menu = ctk.CTkButton(
            self.left_panel,
            width=40,
            height=40,
            fg_color=("#E79CEE", "#C251CC"),
            hover_color=("#E7A2EE", "#CF55DA"),
            text='',
            image=gearwheel_image_ctk,
            command=self.get_scraper_windows_options
        )
        self.options_menu.place(relx=0.9, rely=0.9)

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
            self.left_panel,
            width=40,
            height=40,
            fg_color=("#E79CEE", "#C251CC"),
            hover_color=("#E7A2EE", "#CF55DA"),
            text='' if self.audio_image_ctk_off else 'Music',
            image=self.audio_image_ctk_off, 
        )
        self.mute_audio_btn.place(relx=0.8, rely=0.9)

        right_title = ctk.CTkLabel(
            self.right_panel,
            text="Console", 
            text_color="white",
            font=(self.preferred_font, 20, "bold"),
            fg_color="transparent"
        )
        right_title.place(relx=0.05, rely=0.02)

        self.right_console = ctk.CTkTextbox(
            self.right_panel,
            width=350,
            height=550,
            fg_color=("#FFFFFF", "#000000"),
            text_color='green',
            wrap='word',
            font=(self.preferred_font, self.preferred_size)
        )
        self.right_console.place(relx=0.05, rely=0.1)

    def apply_background_to_tab(self, tab):
        bg_label = ctk.CTkLabel(tab, image=self.bg_image, text="")
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        if not hasattr(self, 'tab_backgrounds'):
            self.tab_backgrounds = []
        self.tab_backgrounds.append(bg_label)

    def _on_submit(self):
        self.left_part_select.configure(state='disabled')
        self.left_website_select.configure(state='disabled')
        self._start_scraping()

    def _start_scraping(self):
        search_term = self.left_entry.get().strip()
        if search_term:
            self.right_console.delete(1.0, 'end')
            self.left_scrape_button.configure(state='disabled')
            self.progress_bar['value'] = 0
            self.status_label.configure(text="Starting scrape...")
            self.scraper.start_scraping(search_term)

    def ask_save_dir(self): 
        folder_path = filedialog.askdirectory(title="Select Folder to Save Excel")
        if folder_path:
            self.save_folder = folder_path
            self.settings_manager.set_ui_setting('save_folder', folder_path)
            if hasattr(self, "folder_tooltip"):
                self.folder_tooltip.text = self.save_folder
    
    def update_font_size(self, selected_size):
        self.preferred_size = int(selected_size)
        self.settings_manager.set_ui_setting('preferred_size', self.preferred_size)
        self.update_font_settings()

    def update_font_family(self, selected_family):
        self.preferred_font = selected_family
        self.settings_manager.set_ui_setting('preferred_font', self.preferred_font)
        self.update_font_settings()

    def update_font_settings(self):
        widgets_to_update = [
            (self.left_panel.winfo_children(), True),
            (self.right_panel.winfo_children(), True),
            (self.look_and_feel_panel.winfo_children(), True),
            (self.customize_ui_colors_dialog.winfo_children(), True),
        ]
        
        for container, recursive in widgets_to_update:
            self._update_widgets_font(container, recursive)

    def get_scraper_windows_options(self):
        if self.scraper_options is None or not self.scraper_options.winfo_exists():
            self.scraper_options = ScraperOptionsWindow(self, scraper=self.scraper, settings_manager=self.settings_manager)
        else:
            self.scraper_options.focus()
    
    def _update_widgets_font(self, widgets, recursive=False):
        for widget in widgets:
            if recursive:
                try:
                    children = widget.winfo_children()
                    if children:
                        self._update_widgets_font(children, True)
                except:
                    pass
            
            if isinstance(widget, ctk.CTkLabel):
                current_font = widget.cget("font")
                if isinstance(current_font, tuple) and len(current_font) >= 2:
                    weight = current_font[2] if len(current_font) > 2 else "normal"
                    widget.configure(font=(self.preferred_font, self.preferred_size, weight))
                else:
                    widget.configure(font=(self.preferred_font, self.preferred_size))
                    
            elif isinstance(widget, ctk.CTkEntry):
                widget.configure(font=(self.preferred_font, self.preferred_size))
                
            elif isinstance(widget, ctk.CTkComboBox):
                widget.configure(font=(self.preferred_font, self.preferred_size))
                
            elif isinstance(widget, ctk.CTkTextbox):
                widget.configure(font=(self.preferred_font, self.preferred_size))
                
            elif isinstance(widget, ctk.CTkButton):
                current_font = widget.cget("font")
                if isinstance(current_font, tuple) and len(current_font) >= 2:
                    size = current_font[1] if current_font[1] != 30 else 30
                    widget.configure(font=(self.preferred_font, size))
                else:
                    widget.configure(font=(self.preferred_font, self.preferred_size))

    def update_language(self, selected_langauge):
        self.preferred_language = selected_langauge
        self.settings_manager.set_ui_setting('preferred_language', self.preferred_language)
        print(f"Updated language to: {self.preferred_language}")

    def on_selection(self, selected_value):
        self.selected_pc_part = selected_value
        print(f"Selected: {self.selected_pc_part}")

    def on_selection_instantiate(self, selected_value):
        self.selected_website = selected_value
    
        print(f"DEBUG: Initializing scraper for {self.selected_website}")
    
        try:
            if self.selected_website == "Amazon.com":
                self.scraper = AmazonComScraper('USD', self.update_gui)  
            elif self.selected_website == "Ardes.bg":
                self.scraper = ArdesScraper('BGN', self.update_gui)   
            elif self.selected_website == 'jarcomputers.com':
                self.scraper = JarComputersScraper('BGN', self.update_gui)  
            elif self.selected_website == "Desktop.bg":
                self.scraper = DesktopScraper('BGN', self.update_gui)
            elif self.selected_website == "Plasico.bg":
                self.scraper = PlasicoScraper('BGN', self.update_gui)
            elif self.selected_website == "PIC.bg":
                self.scraper = PICBgScraper('BGN', self.update_gui)
            elif self.selected_website == "Optimal Computers":
                self.scraper = OptimalComputersScraper('BGN', self.update_gui)
            elif self.selected_website == "Xtreme.bg":
                self.scraper = XtremeScraper('BGN', self.update_gui)
            elif self.selected_website == "CyberTrade.bg":
                self.scraper = CyberTradeScraper('BGN', self.update_gui)
            elif self.selected_website == "PcTech.bg":
                self.scraper = PcTechBgScraper('BGN', self.update_gui)
            elif self.selected_website == "Pro.bg":
                self.scraper = ProBgScraper('BGN', self.update_gui)
            elif self.selected_website == "TechnoMall.bg":
                self.scraper = TechnoMallScraper('BGN', self.update_gui)
            elif self.selected_website == "TehnikStore.bg":
                self.scraper = TehnikStoreScraper('BGN', self.update_gui)
            elif self.selected_website == "AllStore.bg":
                self.scraper = AllStoreScraper('BGN', self.update_gui)
            elif self.selected_website == "Senetic.bg":
                self.scraper = SeneticScraper('BGN', self.update_gui)
            elif self.selected_website == "Thx.bg":
                self.scraper = ThxScraper('BGN', self.update_gui)
            elif self.selected_website == "GtComputers.bg":
                self.scraper = GtComputersScraper('BGN', self.update_gui)
            elif self.selected_website == "Ezona.bg":
                self.scraper = EZonaScraper('BGN', self.update_gui)
            elif self.selected_website == "Tova.bg":
                self.scraper = TovaBGScraper('BGN', self.update_gui)
            elif self.selected_website == "Hits.bg":
                self.scraper = HitsBGScraper('BGN', self.update_gui)
            elif self.selected_website == "Amazon.co.uk":
                self.scraper = AmazonCoUkScraper('GBP', self.update_gui)
            elif self.selected_website == "Amazon.de":
                self.scraper = AmazonDeScraper('EUR', self.update_gui)

            self.settings_manager.apply_to_scraper(self.scraper)
            print(f"DEBUG: Scraper created successfully for {self.selected_website}")
           
        except Exception as e:
            print(f"DEBUG: Scraper initialization failed: {e}")
    
    def update_gui(self, data):
        if not data:  
            return

        self.after(0, self._process_scraper_update, data)

    def _process_scraper_update(self, data):
        try:
            if data['type'] == 'progress':
                self.progress_bar.set(data['value'] / 100)
                self.status_label.configure(
                    text=f"Scraping... {data['value']}% complete",
                    text_color="blue"
                )

            elif data['type'] == 'product':
                product = data['data']
                self.all_products.append(product)

                actual_display_text = "\n".join(f"{label} -> {value}" for label, value in product.items()) + f"{'-' * 50}\n"

                display_text = (
                    f"GPU Found:\n"
                    f"• Title: {product['title']}\n"
                    f"• Price: {product.get('price', 'N/A')}\n"
                    f"• URL: {product.get('url', 'N/A')}\n"
                    f"• Brand: {product.get('brand', 'N/A')}\n"
                    f"• GPU model: {product.get('gpu_model', 'N/A')}\n"
                    f"• Graphics Coprocessor: {product.get('graphics_coprocessor', 'N/A')}\n"
                    f"• Graphics Ram size: {product.get('graphics_ram_size', 'N/A')}\n"
                    f"• GPU clock speed: {product.get('gpu_clock_speed', 'N/A')}\n"
                    f"• Video Output resolution: {product.get('video_output_resolution', 'N/A')}\n"
                    f"• Page: {data.get('page', 'N/A')}\n"
                    f"{'-' * 50}\n"
                )
                self.right_console.insert('end', actual_display_text)
                self.right_console.see('end') 

            elif data['type'] == 'error':
                self.right_console.insert('end', f"ERROR: {data['message']}\n\n")
                self.status_label.configure(text=f"Error: {data['message']}", text_color="red")
                self.progress_bar.set(0)

            elif data['type'] == 'complete':
                self.status_label.configure(text="Scraping completed successfully!", text_color="green")

                for product in self.all_products:
                    if 'price' in product and product['price'] != "N/A":
                        try:
                            price_str = str(product['price']).split('/')[0].strip()

                            for symbol in ["лв", "$", "€", "£", "¥", "USD", "EUR", "BGN", "JPY"]:
                                price_str = price_str.replace(symbol, "")

                            price_str = price_str.replace(",", "").replace(" ", "")
                            original_price = float(price_str)

                            converted_price = convert_currency(
                                original_price,
                                self.scraper.website_currency, 
                                self.preferred_currency
                            )

                            print(f"Converted {original_price} {self.scraper.website_currency} to {converted_price} {self.preferred_currency}")
                            formatted_price = f"{self.currency_symbol}{converted_price:.2f}"
                            product['price'] = formatted_price
                        except Exception as e:
                            print(f"Currency conversion error for {product['title']}: {str(e)}")
                            continue

                tm.TableMaker(data=self.all_products, website_scraped=self.selected_website, output_folder=self.save_folder, pc_part_selected=self.selected_pc_part, currency_symbol=self.currency_symbol)
                self.progress_bar.set(1.0)

        except Exception as e:
            self.right_console.insert('end', f"GUI Update Error: {str(e)}\n\n")
            self.status_label.configure(text=f"Update Error: {str(e)}", text_color="red")

    def setup_settings_tab(self, tab):
        self.look_and_feel_panel = ctk.CTkFrame(
            self.settings_tab, 
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
            font=(self.preferred_font, 20, "bold"),
            fg_color="transparent"
        )
        look_and_feel_label.place(relx=0.35, rely=0.02)
        
        font_label = ctk.CTkLabel(
            self.look_and_feel_panel,
            text="Font settings", 
            text_color="white",
            font=(self.preferred_font, 20, "bold"),
            fg_color="transparent"
        )
        font_label.place(relx=0.1, rely=0.1)

        font_frame = ctk.CTkFrame(
            self.settings_tab, 
            width=400, 
            height=700, 
            fg_color="#1A1A1A",
            border_width=2,
            border_color=("#BA61C3", "#CF55DA"),
            corner_radius=12,
        )
        font_frame.place(x=790, y=130, relwidth=0.3, relheight=0.23)

        font_family = ctk.CTkLabel(
            font_frame,
            text="Font Family", 
            text_color="white",
            font=(self.preferred_font, 15, "bold"),
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
            border_color=("#E599F0", "#592461"),  
            text_color=("black", "white"), 
            button_color=("#3B8ED0", "#1F6AA5"),  
            dropdown_fg_color=("#FFFFFF", "#1A1A1A"),  
            dropdown_text_color=("black", "white"),
            state='readonly',
            command=self.update_font_family,
            font=(self.preferred_font, self.preferred_size)
        )
        self.font_family_select.set("Verdana")
        self.font_family_select.place(relx=0.4, rely=0.05)

        language_label = ctk.CTkLabel(
            font_frame,
            text="Language", 
            text_color="white",
            font=(self.preferred_font, 15, "bold"),
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
            border_color=("#E599F0", "#592461"),  
            text_color=("black", "white"), 
            button_color=("#3B8ED0", "#1F6AA5"),  
            dropdown_fg_color=("#FFFFFF", "#1A1A1A"),  
            dropdown_text_color=("black", "white"),
            state='readonly',
            command=self.update_language,
            font=(self.preferred_font, self.preferred_size)
        )
        self.language_select.set("en-US")
        self.language_select.place(relx=0.4, rely=0.35)
        
        font_size_label = ctk.CTkLabel(
            font_frame,
            text="Font Size", 
            text_color="white",
            font=(self.preferred_font, 15, "bold"),
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
            border_color=("#E599F0", "#592461"),  
            text_color=("black", "white"), 
            button_color=("#3B8ED0", "#1F6AA5"),  
            dropdown_fg_color=("#FFFFFF", "#1A1A1A"),  
            dropdown_text_color=("black", "white"),
            state='readonly',
            command=self.update_font_size,
            font=(self.preferred_font, self.preferred_size)
        )
        self.font_size_select.set("15")
        self.font_size_select.place(relx=0.4, rely=0.65)
    
        self.customize_ui_colors_dialog = ctk.CTkFrame(
            self.settings_tab, 
            width=400,
            height=1000,
            fg_color=("#1A1A1A", "#2D2D2D"),  
            border_width=2,
            border_color=("#3A3A3A", "#4A4A4A"),
            corner_radius=15
        )
        self.customize_ui_colors_dialog.place(x=25, y=35, relwidth=0.6, relheight=0.9)
    
        self.setup_ui_colors_customization()

    def setup_ui_colors_customization(self):
        title_label = ctk.CTkLabel(
            self.customize_ui_colors_dialog,
            text="UI Colors & Theme",
            text_color=("black", "white"),
            font=(self.preferred_font, 22, "bold"),
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
            font=(self.preferred_font, 16, "bold"),
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
            font=(self.preferred_font, 14),
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
            font=(self.preferred_font, 14),
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
            font=(self.preferred_font, 14),
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
            font=(self.preferred_font, self.preferred_size, "bold"),
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
            font=(self.preferred_font, self.preferred_size),
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
            font=(self.preferred_font, self.preferred_size),
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
            font=(self.preferred_font, 14),
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
            font=(self.preferred_font, self.preferred_size),
            width=100,
            fg_color=("#3B8ED0", "#1F6AA5"),
            command=self.pick_secondary_color
        )
        self.secondary_color_btn.grid(row=1, column=2, pady=(10, 0))
    
        preset_colors_label = ctk.CTkLabel(
            color_picker_frame,
            text="Quick Presets:",
            text_color=("black", "white"),
            font=(self.preferred_font, self.preferred_size),
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
            font=(self.preferred_font, 14),
            fg_color=("#FF6B6B", "#FF4757"),
            hover_color=("#FF5252", "#FF3838"),
            text_color="white",
            height=40,
            command=self.reset_to_defaults
        )
        reset_button.place(relx=0.05, rely=0.92, relwidth=0.9)
    
    def reset_to_defaults(self):
        self.settings_manager.settings = self.settings_manager.default_settings.copy()
        self.settings_manager.save_settings()

        self.settings_manager.create_default_theme()
        ctk.set_default_color_theme(self.settings_manager.get_theme_path())
        
        self.preferred_currency = self.settings_manager.get('preferred_currency')
        self.price_format = self.settings_manager.get('price_format')
        self.preferred_language = self.settings_manager.get_ui_setting('preferred_language')
        self.preferred_size = self.settings_manager.get_ui_setting('preferred_size')
        self.preferred_browser = self.settings_manager.get('preferred_browser')
        self.preferred_theme = self.settings_manager.get_ui_setting('preferred_theme')
        self.preferred_font = self.settings_manager.get_ui_setting('preferred_font')
        self.save_folder = self.settings_manager.get_ui_setting('save_folder')
        self.primary_color = self.settings_manager.get_ui_setting('primary_color')
        self.secondary_color = self.settings_manager.get_ui_setting('secondary_color')
    
        self.primary_color_display.configure(fg_color=self.primary_color)
        self.secondary_color_display.configure(fg_color=self.secondary_color)
        ctk.set_appearance_mode(self.preferred_theme.lower())
    
        if hasattr(self, 'font_family_select'):
            self.font_family_select.set(self.preferred_font)
        if hasattr(self, 'font_size_select'):
            self.font_size_select.set(str(self.preferred_size))
    
        self.apply_custom_colors()
        self.update_font_settings()
        self.call_new_instance_if_needed()
    
    print("Reset all settings to defaults")

    def change_theme(self, theme):
        self.preferred_theme = theme
        self.settings_manager.set_ui_setting('preferred_theme', theme)
        ctk.set_appearance_mode(theme.lower())
        print(f"Theme changed to: {theme}")

    def pick_primary_color(self):
        color = self.ask_color()
        if color:
            self.primary_color = color
            self.settings_manager.set_ui_setting('primary_color', color)
            self.primary_color_display.configure(fg_color=color)
            self.apply_custom_colors()

    def pick_secondary_color(self):
        color = self.ask_color()
        if color:
            self.secondary_color = color
            self.settings_manager.set_ui_setting('secondary_color', color)
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
        self.settings_manager.set_ui_setting('primary_color', primary)
        self.settings_manager.set_ui_setting('secondary_color', secondary)
        self.primary_color_display.configure(fg_color=primary)
        self.secondary_color_display.configure(fg_color=secondary)
        self.apply_custom_colors()

    def apply_custom_colors(self):
        try:
            self.settings_manager.update_theme()
            ctk.set_default_color_theme(self.settings_manager.get_theme_path())
            self.update_widget_colors()
            print(f"Applied custom colors: Primary {self.primary_color}, Secondary {self.secondary_color}")
        except Exception as e:
            print(f"Error applying custom colors: {e}")

    def update_widget_colors(self):
        for widget in self.winfo_children():
            self._update_widget_colors_recursive(widget)

    def _update_widget_colors_recursive(self, widget):
        if hasattr(widget, '_is_preset_button') and widget._is_preset_button:
            return
    
        if isinstance(widget, ctk.CTkButton):
            widget.configure(fg_color=self.primary_color, hover_color=self.secondary_color)

        if isinstance(widget, ctk.CTkProgressBar):
            widget.configure(fg_color=self.primary_color, progress_color=self.secondary_color)

        if isinstance(widget, ctk.CTkComboBox):
            widget.configure(button_color=self.primary_color, button_hover_color=self.secondary_color)

        if isinstance(widget, ctk.CTkFrame):
            widget.configure(border_color=self.primary_color)

        for child in widget.winfo_children():
            self._update_widget_colors_recursive(child)
        

    def create_custom_theme(self):
        config_dir = self.settings_manager.get_config_directory()
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
            }
        }

        try:
            with open(theme_path, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=4, ensure_ascii=False)
            print(f"Custom theme saved to {theme_path}")
            return theme_path
        except Exception as e:
            print(f"Error saving custom theme: {e}")
            return None
    
    def setup_info_tab(self, tab):
        info_label = ctk.CTkLabel(tab, text="Application Information", 
                            font=(self.preferred_font, 20, "bold"))
        info_label.pack(pady=20)
    
        info_text = ctk.CTkTextbox(tab, wrap="word", font=(self.preferred_font, self.preferred_size))
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

    def on_currency_change(self, currency):
        self.preferred_currency = currency
        currency_symbols = {
            "BGN": "лв",
            "USD": "$", 
            "EUR": "€",
            "GBP": "£"
        }
        self.currency_symbol = currency_symbols.get(currency, "лв")

    def on_theme_change(self, theme):
        self.preferred_theme = theme
        ctk.set_appearance_mode(theme.lower())

    def on_browser_change(self, browser):
        self.preferred_browser = browser

    def refresh_theme(self):
        """Refresh the theme application"""
        try:
            theme_path = self.settings_manager.get_theme_path()
            if os.path.exists(theme_path):
                print("Theme updated. Restart application to see full changes.")
        except Exception as e:
            print(f"Error refreshing theme: {e}")

    def on_closing(self):
        print("Closing application...")
        
        if self.scraper:
            print("Stopping scraper...")
            try:
                self.scraper.stop_scraping()
            except Exception as e:
                print(f"Error stopping scraper: {e}")
        
        print("Destroying window...")
        self.destroy()

if __name__ == "__main__":
    app = GUI()
    app.mainloop()