import customtkinter as ctk

class ScraperOptionsWindow(ctk.CTkToplevel):
    def __init__(self, master=None, scraper=None):
        super().__init__(master)
        self.scraper = scraper

        self.geometry("520x700")
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

        self.scroll_frame = ctk.CTkScrollableFrame(self, width=480, height=560)
        self.scroll_frame.pack(padx=20, pady=10, fill="both", expand=True)

        ctk.CTkLabel(
            self.scroll_frame, text="General Settings", font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(10, 5))

        ctk.CTkLabel(self.scroll_frame, text="Preferred Browser:").pack(anchor="w", padx=5)
        self.browser_menu = ctk.CTkOptionMenu(
            self.scroll_frame, values=["Chrome", "Firefox", "Edge", "Safari"]
        )
        self.browser_menu.set("Chrome")
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
        self.max_pages_slider.set(10)
        self.max_pages_slider.pack(side="left", fill="x", expand=True)
        self.max_pages_count = ctk.CTkLabel(value_frame, text="10")
        self.max_pages_count.pack(side="left", padx=10)

        ctk.CTkLabel(self.scroll_frame, text="Delay Between Requests (seconds):").pack(anchor="w", padx=5)
        delay_frame = ctk.CTkFrame(self.scroll_frame)
        delay_frame.pack(fill="x", padx=5, pady=(0, 5))
        self.delay_slider = ctk.CTkSlider(delay_frame, from_=0.5, to=10, number_of_steps=95, command=self.update_delay_value)
        self.delay_slider.set(2)
        self.delay_slider.pack(side="left", fill="x", expand=True)
        self.delay_value_label = ctk.CTkLabel(delay_frame, text="2.0s")
        self.delay_value_label.pack(side="left", padx=10)

        ctk.CTkLabel(self.scroll_frame, text="Random Delay Multiplier Range:").pack(anchor="w", padx=5)
        rand_frame = ctk.CTkFrame(self.scroll_frame)
        rand_frame.pack(fill="x", padx=5, pady=(0, 5))
        self.random_slider = ctk.CTkSlider(rand_frame, from_=1.0, to=3.0, number_of_steps=20, command=self.update_random_value)
        self.random_slider.set(1.5)
        self.random_slider.pack(side="left", fill="x", expand=True)
        self.random_value_label = ctk.CTkLabel(rand_frame, text="1.5×")
        self.random_value_label.pack(side="left", padx=10)

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

        ctk.CTkLabel(
            self.scroll_frame, text="Output & Logging", font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(20, 5))

        ctk.CTkLabel(self.scroll_frame, text="Save Results As:").pack(anchor="w", padx=5)
        self.output_format_menu = ctk.CTkOptionMenu(
            self.scroll_frame, values=["JSON", "CSV", "Excel"]
        )
        self.output_format_menu.set("JSON")
        self.output_format_menu.pack(padx=5, pady=5, fill="x")

        self.debug_switch = ctk.CTkSwitch(self.scroll_frame, text="Enable Debug Logs")
        self.debug_switch.pack(anchor="w", padx=5, pady=10)

        self.auto_close_switch = ctk.CTkSwitch(self.scroll_frame, text="Auto-close browser after scraping")
        self.auto_close_switch.pack(anchor="w", padx=5, pady=10)

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
        return {
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
