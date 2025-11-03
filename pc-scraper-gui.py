import customtkinter as ctk
from PIL import Image, ImageFilter
from tkinter import filedialog
from dotenv import load_dotenv
import os
import threading
import sys
import TableMaker as tm

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
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.selected_website = "Desktop.bg"
        self.scraper = None

        self.preferred_currency = "BGN"
        self.currency_format = "0.00"
        self.currency_symbol = "лв"
        self.preferred_language = "en-US"
        self.preferred_size = 12
        self.preferred_browser = "Chrome"
        self.preferred_theme = "Light"
        self.preferred_font = "Times New Roman"
        self.save_folder = os.path.join(os.path.expanduser("~"), "Desktop")
        self.selected_pc_part = "GPU"

        self.all_products = []

        self.setup_background()
        self.create_panels()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_background(self):
        bg_image_path = resource_path("images/nebula-star.png")
        pil_image = Image.open(bg_image_path).convert("RGB")
        
        pil_image = pil_image.resize((1200, 700))
        blurred = pil_image.filter(ImageFilter.GaussianBlur(radius=5))

        overlay = Image.new("RGB", blurred.size, (255, 255, 255))
        self.blended_bg = Image.blend(blurred, overlay, alpha=0.2)
        
        self.bg_image = ctk.CTkImage(light_image=self.blended_bg, size=(1200, 700))
        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def create_panels(self):
        self.left_panel = ctk.CTkFrame(
            self, 
            width=500, 
            height=700,
            fg_color=("#FFFFFF", "#1A1A1A"),
            border_width=2,
            border_color=("#FFFFFF", "#1A1A1A"),
        )
        self.left_panel.place(x=30, y=35, relwidth=0.6, relheight=0.9)

        self.right_panel = ctk.CTkFrame(
            self, 
            width=400, 
            height=700, 
            fg_color="#1A1A1A",  
            border_width=2,
            border_color=("#FFFFFF", "#1A1A1A"),
        )
        self.right_panel.place(x=770, y=35, relwidth=0.33, relheight=0.9)

        self.add_panel_content()

    def add_panel_content(self):
        left_title = ctk.CTkLabel(
            self.left_panel,
            text="PC Parts Web Scraper",
            text_color="white",
            font=("Arial", 20, "bold"),
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
            placeholder_text_color=("#666666", "#888888")
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
            command=self.on_selection
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
            command=self.on_selection_instantiate
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
        self.progress_bar.place(relx=0.05, rely=0.2)

        self.status_label = ctk.CTkLabel(
            self.left_panel,
            text="Ready to scrape...",
            text_color=("black", "white"),
            font=("Arial", 12),
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
            font=('Times New Roman', 30),
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
            font=('Times New Roman', 20),
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
            image=gearwheel_image_ctk
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
            font=("Arial", 20, "bold"),
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
        )
        self.right_console.place(relx=0.05, rely=0.1)
    
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
            if hasattr(self, "folder_tooltip"):
                self.folder_tooltip.text = self.save_folder
    
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