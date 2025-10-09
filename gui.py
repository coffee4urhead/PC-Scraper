import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

#Scrapers
from ardes_scraper import ArdesScraper
from jar_computers_scraper import JarComputersScraper
from scraper import AmazonScraper
from desktop_bg_scraper import DesktopScraper

#Windows
from windows.help_window import HelpWindow
from windows.option_window import OptionsWindow
from windows.font_options_window import WindowsFontOptions

import pygame
import TableMaker as tm

#figure out a way to translate between words in different languages and transfer currencies
class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.selected_website = "Desktop.bg"
        self.scraper = DesktopScraper(self.update_gui)
        self.root.title("GUI App for Scraping General PC Information")
        self.root.geometry("1200x700")

        #Users additional options
        self.preferred_currency = "USD"
        self.currency_format = "0.00"
        self.currency_symbol = "$"
        self.preferred_language = "en-US"
        self.preferred_size = 12
        self.preferred_font = "Comic Sans MS"

        self.selected_pc_part = "GPU"
        pygame.mixer.init()
        self.music_playing = False
        self._setup_gui()
        self.all_products = []
        self.root.mainloop()

    def _setup_gui(self):
        # Background image setup
        image = Image.open("./images/elf.jpg")
        resized_image = image.resize((1200, 700), Image.Resampling.LANCZOS)
        self.background_image = ImageTk.PhotoImage(resized_image)

        canvas = tk.Canvas(self.root, width=1200, height=700, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=self.background_image, anchor="nw")

        # Title label
        label1 = tk.Label(self.root, text="GPU Web Scraper Program",
                          font=("Comic Sans MS", 16, "bold"), bg='white')
        canvas.create_window(600, 50, anchor="center", window=label1)

        # Search label and entry
        label2 = tk.Label(self.root, text="Search GPU model to scrape information:",
                          font=("Comic Sans MS", 12), bg='white')
        canvas.create_window(400, 120, anchor="center", window=label2)

        self.entry = tk.Entry(self.root, width=30, font=("Comic Sans MS", 13, "italic"))
        self.root.bind("<Return>", self._on_key_press)
        canvas.create_window(750, 120, anchor="center", window=self.entry)

        # Buttons
        self.submit_button = tk.Button(self.root, text="Submit", command=self._on_submit,
                                       width=7, font=("Comic Sans MS", 13, "bold"),
                                       height=1, cursor="hand2", padx=10, pady=5)
        canvas.create_window(650, 180, anchor="center", window=self.submit_button)

        #combo box for pc parts
        options = ["Motherboard", 'PSU', 'RAM', 'GPU', 'Case', 'Fans', 'CPU', 'AIO', 'Air Coolers', 'Extension Cables', 'HDD', 'SATA SSD', 'NVME SSD']

        self.combo_scrape_options = ttk.Combobox(self.root, width=20, font=("Comic Sans MS", 13, "bold"), values=options)
        self.combo_scrape_options.current(3)
        self.combo_scrape_options.bind("<<ComboboxSelected>>", self.on_selection)
        canvas.create_window(1050, 120, anchor="center", window=self.combo_scrape_options)

        # combo box for pc websites
        options = ['Ardes.bg', 'jarcomputers.com', 'Desktop.bg', 'Amazon.com', 'Amazon.de', 'Amazon.uk']

        self.combo_website_options = ttk.Combobox(self.root, width=20, font=("Comic Sans MS", 13, "bold"),
                                                 values=options)
        self.combo_website_options.current(2)
        self.combo_website_options.bind("<<ComboboxSelected>>", self.on_selection_instantiate)
        canvas.create_window(1050, 150, anchor="center", window=self.combo_website_options)

        quit_button = tk.Button(self.root, text="Quit", command=self.root.destroy,
                                width=7, font=("Comic Sans MS", 13, "bold"),
                                height=1, cursor="hand2", padx=10, pady=5)
        canvas.create_window(850, 180, anchor="center", window=quit_button)

        self.play_music_button = tk.Button(self.root, text="Play Music", command=self._toggle_music,
                                           width=7, font=("Comic Sans MS", 13, "bold"),
                                           height=1, cursor="hand2", padx=10, pady=5)
        canvas.create_window(750, 180, anchor="center", window=self.play_music_button)

        # Add progress bar
        self.progress_bar = ttk.Progressbar(self.root, orient='horizontal',
                                            length=600, mode='determinate')
        canvas.create_window(600, 230, anchor="center", window=self.progress_bar)

        # Add status label
        self.status_label = tk.Label(self.root, text="Ready to scrape...",
                                     font=("Comic Sans MS", 12), bg='white', padx=7, pady=7)
        canvas.create_window(600, 260, anchor="center", window=self.status_label)

        # Add results text area with scrollbar
        results_frame = tk.Frame(self.root)
        canvas.create_window(600, 480, anchor="center", window=results_frame,
                             width=1000, height=400)

        self.results_text = tk.Text(results_frame, wrap=tk.WORD,
                                    font=("Comic Sans MS", 11),
                                    width=120, height=20)
        scrollbar = tk.Scrollbar(results_frame, command=self.results_text.yview)
        self.results_text.config(yscrollcommand=scrollbar.set)

        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure text tags for styling
        self.results_text.tag_config('error', foreground='red')
        self._create_menu()

    def _create_menu(self):
        # Create menu bar
        menubar = tk.Menu(self.root)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        #Additional user options
        options_menu = tk.Menu(menubar, tearoff=0)
        options_menu.add_command(label="User Options", command=self.show_user_options)
        options_menu.add_command(label="Language & Font", command=self.show_language_options)
        menubar.add_cascade(label="Options", menu=options_menu)

        # Help menu with more options
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Quick Start Guide", command=self.show_about)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about_info)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def show_about_info(self):
        about_win = self.create_new_window("About", "400x300")
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
        label = tk.Label(about_win, text=about_text, justify=tk.CENTER, padx=20, pady=20)
        label.pack()
        back_btn = tk.Button(about_win, text="OK", command=about_win.destroy)
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

    def show_language_options(self):
        if not hasattr(self, '_language_options_window') or not self._language_options_window.window.winfo_exists():
            self._language_options_window = WindowsFontOptions(self)
            self._language_options_window.window.protocol("WM_DELETE_WINDOW", self._on_options_close)
        else:
            self._language_options_window.window.lift()

    def _on_options_close(self):
        if hasattr(self, '_option_window'):
            self._option_window.window.destroy()
            del self._option_window
        if hasattr(self, '_language_options_window'):
            self._language_options_window.window.destroy()
            del self._language_options_window

    def update_options(self, selected_text, format_choice, custom_format=None):
        currency_code = next(
            (code for text, code in self._option_window.currency_options if text == selected_text),
            "USD"
        )
        self.preferred_currency = currency_code
        self.currency_format = custom_format if format_choice == "custom" else "0.00"
        self.currency_symbol = self._get_currency_symbol(currency_code)
        print(
            f"In the parent class information: {self.currency_symbol}{self.preferred_currency} {self.currency_format}")

    def update_language_and_font_options(self, font, size, language):
        self.preferred_language = language
        self.preferred_size = size
        self.preferred_font = font
        print(f"Language info: language: {language}, size: {size}, font: {font}")

    def _get_currency_symbol(self, currency_code):
        """Helper method to get currency symbol"""
        symbols = {
            "USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥",
            "CNY": "¥", "BGN": "лв", "BRL": "R$", "CAD": "$",
            # Add more currency symbols as needed
        }
        return symbols.get(currency_code, currency_code + " ")

    def create_new_window(self, title, size="600x400"):
        """Generic method to create new windows"""
        new_window = tk.Toplevel(self.root)
        new_window.title(title)
        new_window.geometry(size)
        return new_window

    def return_to_main(self, window_to_close):
        """Close the current window and return to main"""
        window_to_close.destroy()
        self.root.deiconify()  # Restore main window if minimized

    def on_selection(self, event=None):
        self.selected_pc_part = self.combo_scrape_options.get()
        print(f"Selected: {self.selected_pc_part}")

    def on_selection_instantiate(self, event):
        self.selected_website = self.combo_website_options.get()

        if self.selected_website == "Amazon.com":
            self.scraper = AmazonScraper(self.update_gui)
        elif self.selected_website == "Ardes.bg":
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # or remove this line for debugging
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )

            # Now pass the driver to the ArdesScraper
            self.scraper = ArdesScraper(self.update_gui, driver=driver)
        elif self.selected_website == 'jarcomputers.com':
            self.scraper = JarComputersScraper(self.update_gui)
        elif self.selected_website == "Desktop.bg":
            self.scraper = DesktopScraper(self.update_gui)

        #add the same logic for the other scrapers

        print(f"Selected website: {self.selected_website}")

    def _toggle_music(self):
        if not self.music_playing:
            pygame.mixer.music.load("./Music/scraping-faster.wav")
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
        if not data:  # Handle empty data
            return

        # Schedule the actual GUI update to run in the main thread
        self.root.after(0, self._process_scraper_update, data)

    def _process_scraper_update(self, data):
        """Process different types of updates from the scraper"""
        try:
            if data['type'] == 'progress':
                # Update progress bar and status
                self.progress_bar['value'] = data['value']
                self.status_label.config(
                    text=f"Scraping... {data['value']}% complete",
                    foreground="blue"
                )

            elif data['type'] == 'product':
                # Add product to results display
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
                self.results_text.see(tk.END)  # Auto-scroll to bottom

            elif data['type'] == 'error':
                # Show error message
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
                # Final completion message
                self.status_label.config(
                    text="Scraping completed successfully!",
                    foreground="green"
                )

                print(self.all_products)
                tm.TableMaker(data=self.all_products, website_scraped=self.selected_website, output_folder=f"{self.selected_website} web search", pc_part_selected=self.selected_pc_part)
                self.progress_bar['value'] = 100
                self.submit_button.config(state=tk.NORMAL)
                self.combo_scrape_options["state"] = tk.NORMAL
                self.combo_website_options["state"] = tk.NORMAL

        except Exception as e:
            # Handle any errors in processing updates
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

GUI()