import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
from dotenv import load_dotenv
import subprocess
import os

from scrapers.scraper import AmazonScraper
from scrapers.ardes_scraper import ArdesScraper
from scrapers.jar_computers_scraper import JarComputersScraper
from scrapers.desktop_bg_scraper import DesktopScraper
from scrapers.plasico_scraper import PlasicoScraper
from scrapers.xtreme_bg_scraper import XtremeScraper
from scrapers.all_store_bg_scraper import AllStoreScraper
from scrapers.pc_tech_scraper import PcTechBgScraper
from scrapers.cyber_trade_scraper import CyberTradeScraper
from scrapers.pic_bg_scraper import PICBgScraper
from scrapers.tehnik_store_scraper import TehnikStoreScraper
from scrapers.pro_bg_scraper import ProBgScraper
from scrapers.senetic_scraper import SeneticScraper
from scrapers.gt_computers import GtComputersScraper
from scrapers.techno_mall_scraper import TechnoMallScraper
from scrapers.thnx_bg_scraper import ThxScraper
from scrapers.optimal_computers_scraper import OptimalComputersScraper

from currency_converter import convert_currency

# TODO: test PlasicoScraper more thoroughly
# TODO: handle Ardes.bg results not found 

from windows.help_window import HelpWindow
from options_window import OptionsWindow
from windows.font_options_window import WindowsFontOptions

import pygame
import TableMaker as tm

load_dotenv() 
API_KEY = os.getenv("UNI_RATE_API_KEY")
API_BASE_URL = os.getenv("BASE_URL")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(BASE_DIR, "images", "elf.jpg")

class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.selected_website = "Desktop.bg"
        self.scraper = None
        self.root.title("GUI App for Scraping General PC Information")
        self.root.geometry("1200x700")

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
        pygame.mixer.init()
        self.music_playing = False
        
        self._setup_gui()
        self.all_products = []
        self.root.mainloop()

    def _setup_gui(self):
        image = Image.open(image_path)
        resized_image = image.resize((1200, 700), Image.Resampling.LANCZOS)
        self.background_image = ImageTk.PhotoImage(resized_image)

        canvas = tk.Canvas(self.root, width=1200, height=700, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=self.background_image, anchor="nw")

        self.label1 = tk.Label(self.root, text="GPU Web Scraper Program",
                          font=(self.preferred_font, 16, "bold"), bg='white')
        canvas.create_window(600, 50, anchor="center", window=self.label1)

        self.label2 = tk.Label(self.root, text="Search GPU model to scrape information:",
                          font=(self.preferred_font, 12), bg='white')
        canvas.create_window(400, 120, anchor="center", window=self.label2)

        self.entry = tk.Entry(self.root, width=30, font=(self.preferred_font, 13, "italic"))
        self.root.bind("<Return>", self._on_key_press)
        canvas.create_window(750, 120, anchor="center", window=self.entry)

        self.submit_button = tk.Button(self.root, text="Submit", command=self._on_submit,
                                   width=7, font=(self.preferred_font, 13, "bold"),
                                   height=1, cursor="hand2", padx=10, pady=5)
        canvas.create_window(650, 180, anchor="center", window=self.submit_button)

        options = ["Motherboard", 'PSU', 'RAM', 'GPU', 'Case', 'Fans', 'CPU', 'AIO', 'Air Coolers', 'Extension Cables', 'HDD', 'SATA SSD', 'NVME SSD']

        self.combo_scrape_options = ttk.Combobox(self.root, width=20, font=(self.preferred_font, 13, "bold"), values=options)
        self.combo_scrape_options.current(3)
        self.combo_scrape_options.bind("<<ComboboxSelected>>", self.on_selection)
        canvas.create_window(1050, 120, anchor="center", window=self.combo_scrape_options)

        options = ['Ardes.bg', 'AllStore.bg', 'GtComputers.bg', 'Thx.bg', 'Senetic.bg', 'TehnikStore.bg', 'Pro.bg', 'TechnoMall.bg', 'PcTech.bg', 'CyberTrade.bg', 'Xtreme.bg', 'Optimal Computers', 'Plasico.bg', 'PIC.bg', 'jarcomputers.com', 'Desktop.bg', 'Amazon.com', 'Amazon.de', 'Amazon.uk']

        self.combo_website_options = ttk.Combobox(self.root, width=20, font=(self.preferred_font, 13, "bold"),
                                             values=options)
        self.combo_website_options.current(2)
        self.combo_website_options.bind("<<ComboboxSelected>>", self.on_selection_instantiate)
        canvas.create_window(1050, 150, anchor="center", window=self.combo_website_options)

        self.quit_button = tk.Button(self.root, text="Quit", command=self.on_closing,
                                width=7, font=(self.preferred_font, 13, "bold"),
                                height=1, cursor="hand2", padx=10, pady=5)
        canvas.create_window(850, 180, anchor="center", window=self.quit_button)

        self.play_music_button = tk.Button(self.root, text="Play Music", command=self._toggle_music,
                                       width=7, font=(self.preferred_font, 13, "bold"),
                                       height=1, cursor="hand2", padx=10, pady=5)
        canvas.create_window(750, 180, anchor="center", window=self.play_music_button)

        self.folder_label = tk.Label(self.root, text=f"Save folder: {self.save_folder}",
                         font=(self.preferred_font, 10), bg='white')
        canvas.create_window(450, 180, anchor="center", window=self.folder_label)

        self.select_folder_button = tk.Button(
            self.root,
            text="Select Save Folder",
            command=self.ask_save_dir,
            width=15,
            font=(self.preferred_font, 12, "bold"),
            cursor="hand2"
        )
        canvas.create_window(200, 180, anchor="center", window=self.select_folder_button)

        self.progress_bar = ttk.Progressbar(self.root, orient='horizontal',
                                        length=600, mode='determinate')
        canvas.create_window(600, 230, anchor="center", window=self.progress_bar)

        self.status_label = tk.Label(self.root, text="Ready to scrape...",
                                 font=(self.preferred_font, 12), bg='white', padx=7, pady=7)
        canvas.create_window(600, 260, anchor="center", window=self.status_label)

        results_frame = tk.Frame(self.root)
        canvas.create_window(600, 480, anchor="center", window=results_frame,
                         width=1000, height=400)

        self.results_text = tk.Text(results_frame, wrap=tk.WORD,
                                font=(self.preferred_font, 11),
                                width=120, height=20)
        scrollbar = tk.Scrollbar(results_frame, command=self.results_text.yview)
        self.results_text.config(yscrollcommand=scrollbar.set)

        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.results_text.tag_config('error', foreground='red')
        self._create_menu()

    def create_new_window(self, title, size="600x400"):
        """Generic method to create new windows with current font settings"""
        new_window = tk.Toplevel(self.root)
        new_window.title(title)
        new_window.geometry(size)
    
        new_window.option_add('*Font', (self.preferred_font, self.preferred_size))
    
        return new_window
    
    def _create_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.on_closing)
        menubar.add_cascade(label="File", menu=file_menu)

        options_menu = tk.Menu(menubar, tearoff=0)
        options_menu.add_command(label="User Options", command=self.show_user_options)
        menubar.add_cascade(label="Options", menu=options_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Quick Start Guide", command=self.show_about)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about_info)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def ask_save_dir(self): 
        folder_path = filedialog.askdirectory(title="Select Folder to Save Excel")
        if folder_path:
            self.save_folder = folder_path
            self.folder_label.config(text=f"Save folder: {self.save_folder}")

    def show_about_info(self):
        about_win = self.create_new_window("About", "600x500")
        about_text = """Web Scraper Application
    Version 1.0
    Developed by Coffee4urhead

    Features:
    - Multi-website scraping
    - Real-time updates
    - Data export capabilities
    - Data integrity checks
    - Data processing at another level
    """
        label = tk.Label(about_win, text=about_text, justify=tk.CENTER, 
                    padx=20, pady=20, font=(self.preferred_font, self.preferred_size))
        label.pack()
        back_btn = tk.Button(about_win, text="OK", command=about_win.destroy,
                                         font=(self.preferred_font, self.preferred_size))
        back_btn.pack(pady=10)

    def show_about(self):
        """Show the help/about window"""
        if not hasattr(self, '_help_window') or not self._help_window.window.winfo_exists():
            self._help_window = HelpWindow(self)
        else:
            self._help_window.window.lift()

    def show_user_options(self):
        if not hasattr(self, '_option_window') or not self._option_window.window.winfo_exists():
            self._option_window = OptionsWindow(self)
            self._option_window.window.protocol("WM_DELETE_WINDOW", self._on_options_close)
        else:
            self._option_window.window.lift()

    def _on_options_close(self):
        if hasattr(self, '_option_window'):
            self._option_window.window.destroy()
            del self._option_window
        if hasattr(self, '_language_options_window'):
            self._language_options_window.window.destroy()
            del self._language_options_window

    def update_options(self, selected_text, format_choice, custom_format=None, browser=None, theme=None):
        currency_code = next(
            (code for text, code in self._option_window.currency_options if text == selected_text),
            "USD"
        )
        self.preferred_currency = currency_code
        self.currency_format = custom_format if format_choice == "custom" else "0.00"
        self.currency_symbol = self._get_currency_symbol(currency_code)
    
        if browser:
            self.preferred_browser = browser
        if theme:
            self.preferred_theme = theme
            self._apply_theme(theme)
        
        self.update_fonts()
        print(f"Settings updated - Currency: {self.currency_symbol}{self.preferred_currency}, Format: {self.currency_format}, Browser: {getattr(self, 'preferred_browser', 'Not set')}, Theme: {getattr(self, 'preferred_theme', 'Not set')}")

    def _get_currency_symbol(self, currency_code):
        """Helper method to get currency symbol"""
        symbols = {
            "USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥",
            "CNY": "¥", "BGN": "лв", "BRL": "R$", "CAD": "$",
        }
        return symbols.get(currency_code, currency_code + " ")

    def return_to_main(self, window_to_close):
        """Close the current window and return to main"""
        window_to_close.destroy()
        self.root.deiconify()  

    def on_selection(self, event=None):
        self.selected_pc_part = self.combo_scrape_options.get()
        print(f"Selected: {self.selected_pc_part}")

    def on_selection_instantiate(self, event):
        self.selected_website = self.combo_website_options.get()
    
        print(f"DEBUG: Initializing scraper for {self.selected_website}")
    
        try:
            if self.selected_website == "Amazon.com":
                self.scraper = AmazonScraper(self.update_gui)  
            elif self.selected_website == "Ardes.bg":
                self.scraper = ArdesScraper(self.update_gui)   
            elif self.selected_website == 'jarcomputers.com':
                self.scraper = JarComputersScraper(self.update_gui)  
            elif self.selected_website == "Desktop.bg":
                self.scraper = DesktopScraper(self.update_gui)
            elif self.selected_website == "Plasico.bg":
                self.scraper = PlasicoScraper(self.update_gui)
            elif self.selected_website == "PIC.bg":
                self.scraper = PICBgScraper(self.update_gui)
            elif self.selected_website == "Optimal Computers":
                self.scraper = OptimalComputersScraper(self.update_gui)
            elif self.selected_website == "Xtreme.bg":
                self.scraper = XtremeScraper(self.update_gui)
            elif self.selected_website == "CyberTrade.bg":
                self.scraper = CyberTradeScraper(self.update_gui)
            elif self.selected_website == "PcTech.bg":
                self.scraper = PcTechBgScraper(self.update_gui)
            elif self.selected_website == "Pro.bg":
                self.scraper = ProBgScraper(self.update_gui)
            elif self.selected_website == "TechnoMall.bg":
                self.scraper = TechnoMallScraper(self.update_gui)
            elif self.selected_website == "TehnikStore.bg":
                self.scraper = TehnikStoreScraper(self.update_gui)
            elif self.selected_website == "AllStore.bg":
                self.scraper = AllStoreScraper(self.update_gui)
            elif self.selected_website == "Senetic.bg":
                self.scraper = SeneticScraper(self.update_gui)
            elif self.selected_website == "Thx.bg":
                self.scraper = ThxScraper(self.update_gui)
            elif self.selected_website == "GtComputers.bg":
                self.scraper = GtComputersScraper(self.update_gui)
                
            print(f"DEBUG: Scraper created successfully for {self.selected_website}")
           
        
        except Exception as e:
            self.status_label.config(text=f"Scraper init failed: {str(e)}", foreground="red")
            print(f"DEBUG: Scraper initialization failed: {e}")

    def _toggle_music(self):
        if not self.music_playing:
            pygame.mixer.music.load("./Music/scraping-faster.mp3")
            pygame.mixer.music.play(loops=-1)
            self.play_music_button.config(text="Pause")
            self.music_playing = True
        else:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
                self.play_music_button.config(text="Resume")
            else:
                pygame.mixer.music.unpause()
                self.play_music_button.config(text="Pause")

    def update_gui(self, data):
        """Handle all updates from the scraper thread in a thread-safe manner"""
        if not data:  
            return

        self.root.after(0, self._process_scraper_update, data)

    def _process_scraper_update(self, data):
        """Process different types of updates from the scraper"""
        try:
            if data['type'] == 'progress':
                self.progress_bar['value'] = data['value']
                self.status_label.config(
                    text=f"Scraping... {data['value']}% complete",
                    foreground="blue"
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
                self.results_text.insert(tk.END, actual_display_text)
                self.results_text.see(tk.END) 

            elif data['type'] == 'error':
                self.results_text.insert(
                    tk.END,
                    f"ERROR: {data['message']}\n\n",
                    'error'
                )
                self.status_label.config(
                    text=f"Error: {data['message']}",
                    foreground="red"
                )
                self.progress_bar['value'] = 0
                self.submit_button.config(state=tk.NORMAL)

            elif data['type'] == 'complete':
                self.status_label.config(
                    text="Scraping completed successfully!",
                    foreground="green"
                )

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
                                'BGN',  
                                self.preferred_currency
                            )

                            print(f"Converted {original_price} BGN to {converted_price} {self.preferred_currency}")
                            formatted_price = f"{self.currency_symbol}{converted_price:.2f}"
                            product['price'] = formatted_price
                        except Exception as e:
                            print(f"Currency conversion error for {product['title']}: {str(e)}")
                            continue

                tm.TableMaker(data=self.all_products, website_scraped=self.selected_website, output_folder=self.save_folder, pc_part_selected=self.selected_pc_part, currency_symbol=self.currency_symbol)
                self.progress_bar['value'] = 100
                self.submit_button.config(state=tk.NORMAL)
                self.combo_scrape_options["state"] = tk.NORMAL
                self.combo_website_options["state"] = tk.NORMAL

        except Exception as e:
            self.results_text.insert(
                tk.END,
                f"GUI Update Error: {str(e)}\n\n",
                'error'
            )
            self.status_label.config(
                text=f"Update Error: {str(e)}",
                foreground="red"
            )

    def _on_key_press(self, event):
        self._start_scraping()

    def _on_submit(self):
        self.combo_scrape_options["state"] = tk.DISABLED
        self.combo_website_options["state"] = tk.DISABLED
        self._start_scraping()

    def _start_scraping(self):
        search_term = self.entry.get().strip()
        if search_term:
            self.results_text.delete(1.0, tk.END)
            self.submit_button.config(state=tk.DISABLED)
            self.progress_bar['value'] = 0
            self.status_label.config(text="Starting scrape...", foreground="blue")
            self.scraper.start_scraping(search_term)
            
    def on_closing(self):
        """Proper cleanup when closing the application"""
        print("DEBUG: Starting application cleanup...")
    
        if self.scraper:
            print("DEBUG: Stopping scraper...")
            self.scraper.stop_scraping()

        print("DEBUG: Cleanup complete, destroying window...")
        self.root.destroy()

    def update_browser_preference(self, browser):
        """Update the preferred browser setting"""
        self.preferred_browser = browser
        print(f"Browser preference updated to: {browser}")

    def update_theme_preference(self, theme):
        """Update the preferred theme setting"""
        self.preferred_theme = theme
        print(f"Theme preference updated to: {theme}")
    
        self._apply_theme(theme)

    def _apply_theme(self, theme):
        """Apply the selected theme to the application"""
        if theme == "Dark":
            self.root.configure(bg='#2b2b2b')
        elif theme == "Light":
            self.root.configure(bg='white')
    def update_fonts(self):
        """Update fonts for all widgets based on current preferences"""
        try:
            print(f"Updating fonts to: {self.preferred_font} {self.preferred_size}") 
        
            label_configs = [
                (self.label1, 16, "bold"),
                (self.label2, 12, "normal"),
                (self.folder_label, 10, "normal"),
                (self.status_label, 12, "normal"),
            ]
        
            for label, size, weight in label_configs:
                if label and label.winfo_exists():
                    if weight == "normal":
                        label.config(font=(self.preferred_font, size))
                    else:
                        label.config(font=(self.preferred_font, size, weight))
        
            button_configs = [
                (self.submit_button, 13, "bold"),
                (self.play_music_button, 13, "bold"),
                (self.quit_button, 13, "bold"),
                (self.select_folder_button, 12, "bold"),
            ]
        
            for button, size, weight in button_configs:
                if button and button.winfo_exists():
                    button.config(font=(self.preferred_font, size, weight))
        
            if self.entry.winfo_exists():
                self.entry.config(font=(self.preferred_font, 13, "italic"))
        
            if self.combo_scrape_options.winfo_exists():
                self.combo_scrape_options.config(font=(self.preferred_font, 13, "bold"))
        
            if self.combo_website_options.winfo_exists():
                self.combo_website_options.config(font=(self.preferred_font, 13, "bold"))

            if self.results_text.winfo_exists():
                self.results_text.config(font=(self.preferred_font, 11))
        
            print(f"Fonts successfully updated to: {self.preferred_font} {self.preferred_size}")
        
        except Exception as e:
            print(f"Error updating fonts: {e}")

if __name__ == "__main__":
    GUI()