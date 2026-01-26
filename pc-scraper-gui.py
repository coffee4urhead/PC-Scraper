import customtkinter as ctk
from tkinter import filedialog
from dotenv import load_dotenv
import os
import threading
import traceback
import sys

from settings_manager import SettingsManager
from FileCreators.TableMaker import TableMaker as tm
from scrapers.cpu_memory_manager import CPUMemoryManagerClass
from FileCreators import JSON_creator as jsc
from FileCreators import CSV_creator as cs
from windows.scraper_options_window import ScraperOptionsWindow
from gui_classes.setup_gui_main import SetupGUI
from currency_converter import RealCurrencyConverter
from scrapers.desktop_bg_scraper import DesktopScraper

from graph_comparer import GraphComparer
from historical_comparer import HistoricalComparison

load_dotenv()
def resource_path(relative_path): 
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else: base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

class GUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PC Scraper GUI")
        self.geometry("1200x700")
        ctk.set_default_color_theme('blue')
        self.converter = RealCurrencyConverter()
        self.settings_manager = SettingsManager()
        self.gui = SetupGUI(self)
        self.currency_mapping = {
            "🇺🇸 USD - US Dollar": "USD",
            "🇪🇺 EUR - Euro": "EUR", 
            "🇬🇧 GBP - British Pound": "GBP",
            "🇯🇵 JPY - Japanese Yen": "JPY",
            "🇨🇳 CNY - Chinese Yuan": "CNY",
            "🇨🇦 CAD - Canadian Dollar": "CAD",
            "🇦🇺 AUD - Australian Dollar": "AUD",
            "🇨🇭 CHF - Swiss Franc": "CHF",
            "🇧🇬 BGN - Bulgarian Lev": "BGN",
            "🇧🇷 BRL - Brazilian Real": "BRL",
            "🇨🇿 CZK - Czech Koruna": "CZK",
            "🇩🇰 DKK - Danish Krone": "DKK",
            "🇭🇰 HKD - Hong Kong Dollar": "HKD",
            "🇭🇺 HUF - Hungarian Forint": "HUF",
            "🇮🇳 INR - Indian Rupee": "INR",
            "🇮🇩 IDR - Indonesian Rupiah": "IDR",
            "🇮🇱 ILS - Israeli Shekel": "ILS",
            "🇰🇷 KRW - South Korean Won": "KRW",
            "🇲🇾 MYR - Malaysian Ringgit": "MYR",
            "🇲🇽 MXN - Mexican Peso": "MXN",
            "🇳🇿 NZD - New Zealand Dollar": "NZD",
            "🇳🇴 NOK - Norwegian Krone": "NOK",
            "🇵🇭 PHP - Philippine Peso": "PHP",
            "🇵🇱 PLN - Polish Zloty": "PLN",
            "🇷🇴 RON - Romanian Leu": "RON",
            "🇷🇺 RUB - Russian Ruble": "RUB",
            "🇸🇬 SGD - Singapore Dollar": "SGD",
            "🇿🇦 ZAR - South African Rand": "ZAR",
            "🇸🇪 SEK - Swedish Krona": "SEK",
            "🇹🇭 THB - Thai Baht": "THB",
            "🇹🇷 TRY - Turkish Lira": "TRY",
            "🇦🇪 AED - Emirati Dirham": "AED"
        }

        self.currency_symbols = {
            "USD": "$",           
            "EUR": "€",           
            "GBP": "£",           
            "JPY": "¥",          
            "CNY": "¥",         
            "CAD": "C$",          
            "AUD": "A$",          
            "CHF": "CHF",         
            "BGN": "лв",          
            "BRL": "R$",          
            "CZK": "Kč",          
            "DKK": "kr",          
            "HKD": "HK$",         
            "HUF": "Ft",          
            "INR": "₹",           
            "IDR": "Rp",         
            "ILS": "₪",           
            "KRW": "₩",           
            "MYR": "RM",          
            "MXN": "Mex$",        
            "NZD": "NZ$",         
            "NOK": "kr",          
            "PHP": "₱",           
            "PLN": "zł",          
            "RON": "lei",         
            "RUB": "₽",           
            "SGD": "S$",          
            "ZAR": "R",          
            "SEK": "kr",          
            "THB": "฿",           
            "TRY": "₺",           
            "AED": "د.إ",         
        }
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
        self.scraper_list = []
        self.cpu_manager = CPUMemoryManagerClass()
        self.website_selection_limit = self.cpu_manager.get_optimal_worker_count()
        self.selected_websites = []
        self.settings_manager.apply_to_scraper(self.scraper)
        self.all_products = []
        self.scraper_options = None
        self.setup_gui()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self._on_website_selection = self._handle_website_selection
        self.on_selection = self._handle_part_selection
        self._connect_gui_callbacks()
        self.apply_custom_colors = self.gui.apply_custom_colors
        self.after(100, self.apply_custom_colors)

    def _handle_website_selection(self, selected_website):
        """Handle website selection"""
        print(f"Website selected: {selected_website}")
        self.selected_website = selected_website
        
        if hasattr(self, 'gui') and hasattr(self.gui, 'on_selection_instantiate'):
            return self.gui.on_selection_instantiate(selected_website)
        return None
    
    def _handle_part_selection(self, selected_part):
        """Handle part selection"""
        print(f"Part selected: {selected_part}")
        self.selected_pc_part = selected_part
    
    def _handle_scraping(self):
        """Handle scraping start"""
        print("Starting scraping...")
        self._start_scraping()
        
    def _connect_gui_callbacks(self):
        """Connect the GUI callbacks to your methods"""
        if hasattr(self.gui, 'begin_comparison_button'):
            self.gui.begin_comparison_button.configure(command=self._make_historical_comparison)
        
        if hasattr(self.gui, 'refresh_gui_button'):
            self.gui.refresh_gui_button.configure(command=self.setup_gui)
        
        if hasattr(self, 'left_website_select'):
            self.left_website_select.configure(command=self._on_website_selection)
        
        if hasattr(self, 'left_part_select'):
            self.left_part_select.configure(command=self.on_selection)
        
        if hasattr(self, 'left_scrape_button'):
            self.left_scrape_button.configure(command=self._start_scraping)

        if hasattr(self, 'left_select_folder_button'):
            self.left_select_folder_button.configure(command=self.ask_save_dir)

        if hasattr(self, 'options_menu'):
            self.options_menu.configure(command=self.get_scraper_windows_options)
    
    def setup_gui(self):
        """Setup the entire GUI using the new modular class"""
        self.gui.setup()
        
        print(f"GUI setup complete. Widgets available:")
        print(f"  - Entry: {hasattr(self, 'left_entry')}")
        print(f"  - Console: {hasattr(self, 'right_console')}")
        print(f"  - Scraper: {hasattr(self, 'current_scraper')}")

        if hasattr(self, 'right_console'):
            self.right_console.delete("1.0", "end")
            self.update_gui("GUI initialized successfully. Ready to scrape!")

    def _on_submit(self):
        self.left_part_select.configure(state='disabled')
        self.left_website_select.configure(state='disabled')
        self._start_scraping()

    def _start_scraping(self):
        search_term = self.left_entry.get().strip()
        if search_term:
            self.right_console.delete(1.0, 'end')
            self.reconfigure_back_property(self.left_scrape_button, True)
            self.reconfigure_back_property(self.left_entry, True)
            self.reconfigure_back_property(self.left_website_select, True)
            self.reconfigure_back_property(self.left_part_select, True)
            self.progress_bar['value'] = 0
            self.status_label.configure(text="Starting scrape...")
            self.all_products.clear()
        
            threading.Thread(
                target=self._run_async_scraper,
                args=(search_term,),
                daemon=True
            ).start()

    def _run_async_scraper(self, search_term):
        """Run the async scraper in a background thread"""
        import asyncio
    
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            loop.run_until_complete(
                self.scraper.start_scraping_async(search_term)
            )
        
        except Exception as e:
            error_msg = f"Scraping error: {str(e)}"
            print(error_msg)

            self.after(0, lambda: self._handle_scraping_error(error_msg))

        finally:
            if loop and not loop.is_closed():
                loop.close()

    def _handle_scraping_error(self, error_message):
        """Handle scraping errors on the main thread"""
        self.status_label.configure(
            text=f"Error: {error_message}", 
            text_color="red"
        )
        self.right_console.insert('end', f"ERROR: {error_message}\n\n")
        self.progress_bar.set(0)

    def ask_save_dir(self): 
        folder_path = filedialog.askdirectory(title="Select Folder to Save Excel", initialdir=self.save_folder)
        if folder_path:
            self.save_folder = folder_path
            self.settings_manager.set_ui_setting('save_folder', folder_path)
            if hasattr(self, "folder_tooltip"):
                self.folder_tooltip.text = self.save_folder
                self.settings_manager.set_ui_setting('save_folder', folder_path)

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
    
    def update_gui(self, data):
        if not data:  
            return

        self.after(0, self._process_scraper_update, data)

    def _process_scraper_update(self, data):
        """Tkinter callback - must be synchronous (remove async)"""
        try:
            if isinstance(data, str):
                self.right_console.insert('end', f"{data}\n")
                self.right_console.see('end')
                return
        
            if not isinstance(data, dict):
                self.right_console.insert('end', f"Unexpected data type: {type(data)} - {str(data)[:100]}...\n")
                self.right_console.see('end')
                return
        
            data_type = data.get('type', 'unknown')
        
            if data_type == 'progress':
                progress_value = data.get('value', 0)
                self.progress_bar.set(progress_value / 100)
                self.status_label.configure(
                    text=f"Scraping... {progress_value}% complete",
                    text_color="blue"
                )

            elif data_type == 'product':
                product = data.get('data', {})
                print(f"DEBUG update_gui called with: {type(data)}")
                print(product)

                if product:
                    self.all_products.append(product)

                    display_text = (
                        f"Product Found:\n"
                        f"• Title: {product.get('title', 'N/A')}\n"
                        f"• Price: {product.get('price', 'N/A')}\n"
                        f"• URL: {product.get('url', 'N/A')}\n"
                        f"• Source: {product.get('source', 'N/A')}\n"
                        f"• Page: {product.get('page', 'N/A')}\n"
                        f"{'-' * 50}\n"
                    )
                    self.right_console.insert('end', display_text)
                    self.right_console.see('end')

            elif data_type == 'error':
                error_message = data.get('message', 'Unknown error')
                self.right_console.insert('end', f"ERROR: {error_message}\n\n")
                self.status_label.configure(text=f"Error: {error_message}", text_color="red")
                self.progress_bar.set(0)

            elif data_type == 'complete':
                self.status_label.configure(text="Processing results...", text_color="orange")
            
                for widget_name in ['left_scrape_button', 'left_entry', 'left_website_select', 'left_part_select']:
                    if hasattr(self, widget_name):
                        widget = getattr(self, widget_name)
                        self.reconfigure_back_property(widget, True)

                threading.Thread(
                    target=self._convert_prices_and_create_excel,
                    daemon=True
                ).start()

            elif data_type == 'status':
                status_message = data.get('message', '')
                if status_message:
                    self.right_console.insert('end', f"STATUS: {status_message}\n")
                    self.right_console.see('end')
                    self.status_label.configure(text=status_message, text_color="blue")

            else:
                self.right_console.insert('end', f"DEBUG: Unknown data type '{data_type}': {str(data)[:200]}...\n")
                self.right_console.see('end')

        except Exception as e:
            error_msg = f"GUI Update Error: {str(e)}\n"
            self.right_console.insert('end', error_msg)
            self.right_console.see('end')
            self.status_label.configure(text=f"Update Error: {str(e)[:50]}", text_color="red")
            print(f"GUI Error: {e}\nData received: {data}")

    def _convert_prices_and_create_excel(self):
        """Run currency conversion and Excel creation in background thread"""
        try:
            for product in self.all_products:
                if 'price' in product and product['price'] != "N/A":
                    try:
                        price_str = str(product['price']).split('/')[0].strip()

                        for symbol in ["лв", "$", "€", "£", "¥", "USD", "EUR", "BGN", "JPY"]:
                            price_str = price_str.replace(symbol, "")

                        price_str = price_str.replace(",", "").replace(" ", "")
                        original_price = float(price_str)

                        converted_price = self.converter.convert_currency(
                            original_price,
                            self.scraper.website_currency, 
                            getattr(self.scraper, 'preferred_currency', 'BGN')
                        )

                        currency_code = getattr(self.scraper, 'preferred_currency', 'BGN')
                        symbol = self.currency_symbols.get(currency_code, "лв") 

                        if converted_price is None:
                            formatted_price = f"лв{original_price:.2f}"  
                            print(f"⚠️ Conversion failed for {product['title']}, using original price")
                        else:
                            formatted_price = f"{symbol}{converted_price:.2f}"
                    
                        product['price'] = formatted_price
                    except Exception as e:
                        print(f"Currency conversion error for {product['title']}: {str(e)}")
                        continue

            currency_code = getattr(self.scraper, 'preferred_currency', 'BGN')
            symbol = self.currency_symbols.get(currency_code, "лв")
            output_format = self.settings_manager.get("output_format", 'Excel')
            print(f"DEBUG: Output format preference: {output_format}")
            print(self.all_products)
            
            if output_format == 'JSON':
                print("JSON preferred!")
                jsc.JSONCreator(
                    data=self.all_products,
                    website_scraped=self.selected_website,
                    output_folder=self.save_folder,
                    pc_part_selected=self.selected_pc_part,
                    currency_symbol=symbol,
                    history_save_preferred=True,
                )

            elif output_format == 'CSV':
                cs.CSVCreator(
                    data=self.all_products, 
                    website_scraped=self.selected_website, 
                    output_folder=self.save_folder, 
                    pc_part_selected=self.selected_pc_part, 
                    currency_symbol=symbol,
                    history_save_preferred=True
                )
            elif output_format == 'Excel':
                tm.TableMaker(
                    data=self.all_products, 
                    website_scraped=self.selected_website, 
                    output_folder=self.save_folder, 
                    pc_part_selected=self.selected_pc_part, 
                    currency_symbol=symbol
                )
        
            self.after(0, self._on_processing_complete)

        except Exception as e:
            print(f"Background processing error: {e}")
            traceback.print_exc()
            error_message = str(e)
            self.after(0, lambda: self.status_label.configure(
                text=f"Processing error: {error_message}", 
                text_color="red"
            ))

    def _on_processing_complete(self):
        """Called on main thread when background processing is done"""
        self.status_label.configure(text="Scraping completed successfully!", text_color="green")
        self.progress_bar.set(1.0)

    def set_second_website_for_comparison(self, value):
        self.second_website_for_comparison = value
        self.settings_manager.set('second_website_for_comparison', value)
        print(f"second website for comparison is {self.second_website_for_comparison}")
        
    def set_first_website_for_comparison(self, value):
        self.first_website_for_comparison = value
        self.settings_manager.set('first_website_for_comparison', value)
        print(f"first website for comparison is {self.first_website_for_comparison}")

    def set_part_comparison(self, part_to_compare):
        self.part_to_compare_historically = part_to_compare
        print(f"We are comparing {self.part_to_compare_historically}")

    def _make_historical_comparison(self):
        """Handle historical comparison with GUI feedback"""
        error_msg = "" 
    
        try:
            output_format = self.settings_manager.get("output_format", 'CSV')
            part_to_compare = self.part_to_compare_historically
            first_website = self.first_website_for_comparison
            second_website = self.second_website_for_comparison
        
            comparison = HistoricalComparison(
                output_format,
                part_to_compare,
                first_website,
                second_website
            )

            result = comparison.get_summary()
        
            if result['status'] == 'ready':
                first_count = len(comparison.first_website_files)
                second_count = len(comparison.second_website_files)
            
                message = (f"✅ Comparison Ready!\n"
                    f"📁 {first_website}: {first_count} files\n"
                    f"📁 {second_website}: {second_count} files\n"
                    f"📊 Ready to compare {part_to_compare} prices")
            
                self._update_comparison_status(message, "green")
                self.current_comparison = comparison
            
                if hasattr(self, 'visualize_button'):
                    self.visualize_button.configure(state="normal")
            
                if hasattr(self, 'visualization_frame'):
                    GraphComparer(result['data'], output_format, self.visualization_frame)
                else:
                    GraphComparer(result['data'], output_format)
            
                print(f"Success: {first_count} vs {second_count} files")
            
            else:  
                error_msg = f"❌ Error: {result['message']}"
                self._update_comparison_status(error_msg, "red")
                print(f"Error: {result['message']}")
            
        except Exception as e:
            error_msg = f"❌ Unexpected error: {str(e)}"
            print(f"Comparison error: {traceback.format_exc()}")
            self._update_comparison_status(error_msg, "red")
    
    def _update_comparison_status(self, message, color="green"):
        """Helper method to update the status label"""
        if hasattr(self, 'comparison_status_label'):
            self.comparison_status_label.configure(
                text=message,
                text_color=color
            )
        else:
            self.comparison_status_label = ctk.CTkLabel(
                self.price_comparison_panel,
                text=message,
                font=(self.preferred_font, 14),
                text_color=color
            )
            self.comparison_status_label.place(relx=0.02, rely=0.12)

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

    def reconfigure_back_property(self, widget, enabled: bool = True):
        if hasattr(widget, 'configure'):
            state_value = "normal" if enabled else "disabled"
            widget.configure(state=state_value)
        else:
            print(f"DEBUG: Widget {widget} doesn't have configure method")

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
            if isinstance(widget, ctk.CTkComboBox):
                widget.configure(
                button_color=self.primary_color,
                button_hover_color=self.secondary_color,
                border_color=self.secondary_color,
                fg_color=("#FFFFFF", "#1A1A1A"),
                text_color=("black", "white"),
                dropdown_fg_color=("#FFFFFF", "#1A1A1A"),
                dropdown_hover_color=(self.primary_color, self.secondary_color),
                dropdown_text_color=("black", "white")
            )

        if isinstance(widget, ctk.CTkEntry):
            widget.configure(
                fg_color=("#FFFFFF", "#1A1A1A"),
                border_color=self.primary_color,
                placeholder_text_color=("grey", "lightgrey"),
                text_color=("black", "white"),
            )

        if isinstance(widget, ctk.CTkFrame):
            widget.configure(border_color=self.primary_color)

        for child in widget.winfo_children():
            self._update_widget_colors_recursive(child)

    def on_closing(self):
        print("Closing application...")
        if self.scraper:
            print("Stopping scraper...")
            try:
                self.scraper.stop_scraping()
            except Exception as e:
                print(f"Error stopping scraper: {e}")

        for widget in self.winfo_children():
            try:
                widget.destroy()
            except Exception as e:
                print(f"Error destroying {widget}: {e}")

        self.quit() 


if __name__ == "__main__":
    app = GUI()
    app.mainloop()