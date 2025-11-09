import customtkinter as ctk

class ScraperOptionsWindow(ctk.CTkToplevel):
    def __init__(self, master=None, scraper=None):
        super().__init__(master)
        self.scraper = scraper

        self.geometry("520x800")
        self.title("🧩 Scraper Settings")
        self.resizable(False, False)
        self.configure(fg_color=("#1E1E1E", "#121212"))

        self.lift()
        self.focus_force()
        self.grab_set()

        title_label = ctk.CTkLabel(
            self, text="Scraper Configuration", font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.pack(pady=(20, 10))

        self.scroll_frame = ctk.CTkScrollableFrame(self, width=480, height=660)
        self.scroll_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # ====================================================
        # General Settings Section
        # ====================================================
        ctk.CTkLabel(
            self.scroll_frame, text="General Settings", font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(20, 5))

        ctk.CTkLabel(self.scroll_frame, text="Preferred Browser:").pack(anchor="w", padx=5)
        self.browser_menu = ctk.CTkOptionMenu(
            self.scroll_frame, values=["Chrome", "Firefox", "Edge", "Safari"]
        )
        self.browser_menu.pack(padx=5, pady=5, fill="x")

        self.headless_switch = ctk.CTkSwitch(
            self.scroll_frame, text="Run in headless mode", onvalue=True, offvalue=False
        )
        self.headless_switch.pack(anchor="w", padx=5, pady=(10, 15))

        ctk.CTkLabel(self.scroll_frame, text="Max Pages to Scrape:").pack(anchor="w", padx=5)
        value_frame = ctk.CTkFrame(self.scroll_frame)
        value_frame.pack(fill="x", padx=5, pady=(0, 5))

        self.max_pages_slider = ctk.CTkSlider(
            value_frame, from_=1, to=100, number_of_steps=99, command=self.update_max_pages_value
        )
        self.max_pages_slider.pack(side="left", fill="x", expand=True)
        self.max_pages_count = ctk.CTkLabel(value_frame, text="10")
        self.max_pages_count.pack(side="left", padx=10)

        ctk.CTkLabel(self.scroll_frame, text="Delay Between Requests (seconds):").pack(anchor="w", padx=5)
        delay_frame = ctk.CTkFrame(self.scroll_frame)
        delay_frame.pack(fill="x", padx=5, pady=(0, 5))
        self.delay_slider = ctk.CTkSlider(delay_frame, from_=0.5, to=10, number_of_steps=95, command=self.update_delay_value)
        self.delay_slider.pack(side="left", fill="x", expand=True)
        self.delay_value_label = ctk.CTkLabel(delay_frame, text="2.0s")
        self.delay_value_label.pack(side="left", padx=10)

        ctk.CTkLabel(self.scroll_frame, text="Random Delay Multiplier Range:").pack(anchor="w", padx=5)
        rand_frame = ctk.CTkFrame(self.scroll_frame)
        rand_frame.pack(fill="x", padx=5, pady=(0, 5))
        self.random_slider = ctk.CTkSlider(rand_frame, from_=1.0, to=3.0, number_of_steps=20, command=self.update_random_value)
        self.random_slider.pack(side="left", fill="x", expand=True)
        self.random_value_label = ctk.CTkLabel(rand_frame, text="1.5×")
        self.random_value_label.pack(side="left", padx=10)

        # ====================================================
        # Filtering Options Section
        # ====================================================
        ctk.CTkLabel(
            self.scroll_frame, text="Filtering Options", font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(20, 5))

        price_frame = ctk.CTkFrame(self.scroll_frame)
        price_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(price_frame, text="Min Price:").pack(side="left", padx=5)
        self.min_price_entry = ctk.CTkEntry(price_frame, width=100)
        self.min_price_entry.pack(side="left", padx=5)
        ctk.CTkLabel(price_frame, text="Max Price:").pack(side="left", padx=5)
        self.max_price_entry = ctk.CTkEntry(price_frame, width=100)
        self.max_price_entry.pack(side="left", padx=5)

        ctk.CTkLabel(self.scroll_frame, text="Exclude Keywords (comma separated):").pack(anchor="w", padx=5)
        self.exclude_entry = ctk.CTkEntry(self.scroll_frame, placeholder_text="e.g. refurbished, used, old")
        self.exclude_entry.pack(padx=5, pady=5, fill="x")

        # ====================================================
        # Output & Logging Section
        # ====================================================
        ctk.CTkLabel(
            self.scroll_frame, text="Output & Logging", font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(20, 5))

        ctk.CTkLabel(self.scroll_frame, text="Save Results As:").pack(anchor="w", padx=5)
        self.output_format_menu = ctk.CTkOptionMenu(
            self.scroll_frame, values=["JSON", "CSV", "Excel"]
        )
        self.output_format_menu.pack(padx=5, pady=5, fill="x")

        self.debug_switch = ctk.CTkSwitch(self.scroll_frame, text="Enable Debug Logs")
        self.debug_switch.pack(anchor="w", padx=5, pady=10)

        self.auto_close_switch = ctk.CTkSwitch(self.scroll_frame, text="Auto-close browser after scraping")
        self.auto_close_switch.pack(anchor="w", padx=5, pady=10)

        # ====================================================
        # Buttons
        # ====================================================
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=15, padx=20, fill="x")

        self.apply_button = ctk.CTkButton(
            button_frame,
            text="✅ Apply Settings",
            height=40,
            corner_radius=12,
            fg_color="#3B82F6",
            hover_color="#2563EB",
            command=self.apply_settings
        )
        self.apply_button.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.save_close_button = ctk.CTkButton(
            button_frame,
            text="💾 Save & Close",
            height=40,
            corner_radius=12,
            fg_color="#22C55E",
            hover_color="#16A34A",
            command=self.save_and_close
        )
        self.save_close_button.pack(side="left", expand=True, fill="x", padx=(5, 0))

        # ====================================================
        # Currency Settings Section
        # ====================================================
        ctk.CTkLabel(
            self.scroll_frame, text="Currency Settings", font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(10, 5))

        ctk.CTkLabel(self.scroll_frame, text="Select Currency:").pack(anchor="w", padx=5)
        self.currency_menu = ctk.CTkOptionMenu(
            self.scroll_frame, 
            values=[
                "🇺🇸 USD - US Dollar", "🇪🇺 EUR - Euro", "🇬🇧 GBP - British Pound", 
                "🇯🇵 JPY - Japanese Yen", "🇨🇳 CNY - Chinese Yuan", "🇨🇦 CAD - Canadian Dollar",
                "🇦🇺 AUD - Australian Dollar", "🇨🇭 CHF - Swiss Franc", "🇧🇬 BGN - Bulgarian Lev",
                "🇧🇷 BRL - Brazilian Real", "🇨🇿 CZK - Czech Koruna", "🇩🇰 DKK - Danish Krone",
                "🇭🇰 HKD - Hong Kong Dollar", "🇭🇺 HUF - Hungarian Forint", "🇮🇳 INR - Indian Rupee",
                "🇮🇩 IDR - Indonesian Rupiah", "🇮🇱 ILS - Israeli Shekel", "🇰🇷 KRW - South Korean Won",
                "🇲🇾 MYR - Malaysian Ringgit", "🇲🇽 MXN - Mexican Peso", "🇳🇿 NZD - New Zealand Dollar",
                "🇳🇴 NOK - Norwegian Krone", "🇵🇭 PHP - Philippine Peso", "🇵🇱 PLN - Polish Zloty",
                "🇷🇴 RON - Romanian Leu", "🇷🇺 RUB - Russian Ruble", "🇸🇬 SGD - Singapore Dollar",
                "🇿🇦 ZAR - South African Rand", "🇸🇪 SEK - Swedish Krona", "🇹🇭 THB - Thai Baht",
                "🇹🇷 TRY - Turkish Lira", "🇦🇪 AED - Emirati Dirham"
            ]
        )
        self.currency_menu.pack(padx=5, pady=5, fill="x")

        self.formatting_var = ctk.StringVar(value="default")
        
        format_frame = ctk.CTkFrame(self.scroll_frame)
        format_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(format_frame, text="Price Formatting:").pack(anchor="w", padx=5, pady=(5, 0))
        
        self.default_format_radio = ctk.CTkRadioButton(
            format_frame, 
            text="Default formatting (0.00)", 
            variable=self.formatting_var, 
            value="default"
        )
        self.default_format_radio.pack(anchor="w", padx=5, pady=2)
        
        self.custom_format_radio = ctk.CTkRadioButton(
            format_frame, 
            text="Custom formatting", 
            variable=self.formatting_var, 
            value="custom",
            command=self._toggle_custom_format
        )
        self.custom_format_radio.pack(anchor="w", padx=5, pady=2)
        
        self.custom_format_frame = ctk.CTkFrame(self.scroll_frame)
        self.custom_format_entry = ctk.CTkEntry(
            self.custom_format_frame, 
            placeholder_text="e.g., 0.000, 0,000, 0#000",
            width=200
        )
        self.custom_format_entry.pack(side="left", padx=5, pady=5)
        
        self.format_examples = ctk.CTkLabel(
            self.custom_format_frame,
            text="Examples: 0.000 → 1234.567\n0,000 → 1234,567\n0#000 → 1234#567",
            font=ctk.CTkFont(size=11),
            justify="left"
        )
        self.format_examples.pack(side="left", padx=5, pady=5)
        
        self.custom_format_frame.pack_forget()
        
        # ====================================================
        # Load current settings after UI is created
        # ====================================================
        self.load_current_settings()

    def load_current_settings(self):
        """Load current scraper settings into the UI"""
        if not self.scraper:
            return

        print("🔄 Loading current scraper settings...")
        
        preferred_currency = getattr(self.scraper, 'preferred_currency', 'BGN')
        price_format = getattr(self.scraper, 'price_format', '0.00')

        for option in self.currency_menu._values:
            if preferred_currency in option:
                self.currency_menu.set(option)
                break
        
        if price_format != "0.00":
            self.formatting_var.set("custom")
            self.custom_format_entry.delete(0, 'end')
            self.custom_format_entry.insert(0, price_format)
            self._toggle_custom_format()  
        else:
            self.formatting_var.set("default")
            self._toggle_custom_format() 

        self.browser_menu.set(getattr(self.scraper, 'preferred_browser', 'Chrome'))
        self.headless_switch.select() if getattr(self.scraper, 'headless', False) else self.headless_switch.deselect()
        
        max_pages = getattr(self.scraper, 'max_pages', 10)
        self.max_pages_slider.set(max_pages)
        self.max_pages_count.configure(text=str(max_pages))
        
        delay = getattr(self.scraper, 'delay_between_requests', 2.0)
        self.delay_slider.set(delay)
        self.delay_value_label.configure(text=f"{delay:.1f}s")
        
        random_multiplier = getattr(self.scraper, 'random_delay_multiplier', 1.5)
        self.random_slider.set(random_multiplier)
        self.random_value_label.configure(text=f"{random_multiplier:.2f}×")

        min_price = getattr(self.scraper, 'min_price', '')
        max_price = getattr(self.scraper, 'max_price', '')
        exclude_keywords = getattr(self.scraper, 'exclude_keywords', '')
        
        self.min_price_entry.delete(0, 'end')
        self.min_price_entry.insert(0, str(min_price))
        
        self.max_price_entry.delete(0, 'end')
        self.max_price_entry.insert(0, str(max_price))
        
        self.exclude_entry.delete(0, 'end')
        self.exclude_entry.insert(0, str(exclude_keywords))

        self.output_format_menu.set(getattr(self.scraper, 'output_format', 'JSON'))
        self.debug_switch.select() if getattr(self.scraper, 'debug_logs', False) else self.debug_switch.deselect()
        self.auto_close_switch.select() if getattr(self.scraper, 'auto_close', True) else self.auto_close_switch.deselect()

        print("✅ Current settings loaded into UI")

    def _toggle_custom_format(self):
        """Show/hide custom format entry based on radio selection"""
        if self.formatting_var.get() == "custom":
            self.custom_format_frame.pack(fill="x", padx=5, pady=5)
        else:
            self.custom_format_frame.pack_forget()

    def update_max_pages_value(self, value):
        self.max_pages_count.configure(text=f"{int(value)}")

    def update_delay_value(self, value):
        self.delay_value_label.configure(text=f"{float(value):.1f}s")

    def update_random_value(self, value):
        self.random_value_label.configure(text=f"{float(value):.2f}×")

    # ====================================================
    # Helper: collect all settings in a dict
    # ====================================================
    def collect_settings(self):
        selected_currency_text = self.currency_menu.get()
        currency_code = "BGN" 
        for option in self.currency_menu._values:
            if option == selected_currency_text:
                parts = option.split(" - ")
                if len(parts) > 1:
                    currency_code = parts[1].strip()
                break
        
        price_format = "0.00"  
        if self.formatting_var.get() == "custom" and self.custom_format_entry.get().strip():
            price_format = self.custom_format_entry.get().strip()
        
        return {
            "preferred_currency": currency_code,
            "price_format": price_format,
            "preferred_browser": self.browser_menu.get(),
            "headless": self.headless_switch.get(),
            "max_pages": int(self.max_pages_slider.get()),
            "delay_between_requests": round(self.delay_slider.get(), 2),
            "random_delay_multiplier": round(self.random_slider.get(), 2),
            "min_price": self.min_price_entry.get(),
            "max_price": self.max_price_entry.get(),
            "exclude_keywords": self.exclude_entry.get(),
            "output_format": self.output_format_menu.get(),
            "debug_logs": self.debug_switch.get(),
            "auto_close": self.auto_close_switch.get(),
        }

    # ====================================================
    # Button actions
    # ====================================================
    def apply_settings(self):
        """Apply settings without closing the window"""
        settings = self.collect_settings()

        if self.scraper:
            for key, value in settings.items():
                setattr(self.scraper, key, value)

        print("✅ Applied Scraper Settings:")
        for k, v in settings.items():
            print(f"  {k}: {v}")

    def save_and_close(self):
        """Apply settings and close the window"""
        self.apply_settings()
        self.destroy()