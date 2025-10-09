import tkinter as tk
from tkinter import ttk

class OptionsWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent.root)
        self.window.title("Additional options")
        self.window.geometry("500x400")

        self.formatting_of_currency = tk.StringVar(value='0.00')
        self.selected_currency = tk.StringVar(value="🇺🇸 USD - US Dollar")
        self.currency_options = None

        self.window.grab_set()
        self.window.transient(parent.root)

        self._setup_ui()

    def _setup_ui(self):
        # Currency formatting section
        currency_section = tk.Label(self.window, text="Choose currency formats",
                                    justify=tk.CENTER, padx=20, pady=20,
                                    font=("Comic Sans MS", 12))
        currency_section.pack()

        # Currency formatting options
        default_formatting = tk.Radiobutton(self.window, text="Use default formatting",
                                            variable=self.formatting_of_currency,
                                            value="default")
        default_formatting.pack()

        custom_formatting = tk.Radiobutton(self.window, text="Use custom formatting",
                                           variable=self.formatting_of_currency,
                                           value="custom", command=self._display_text_box)
        custom_formatting.pack()

        # Currency selection combobox
        self.currency_options = [
            ("🇺🇸 USD - US Dollar", "USD"),
            ("🇪🇺 EUR - Euro", "EUR"),
            ("🇬🇧 GBP - British Pound", "GBP"),
            ("🇯🇵 JPY - Japanese Yen", "JPY"),
            ("🇨🇳 CNY - Chinese Yuan", "CNY"),
            ("🇨🇦 CAD - Canadian Dollar", "CAD"),
            ("🇦🇺 AUD - Australian Dollar", "AUD"),
            ("🇨🇭 CHF - Swiss Franc", "CHF"),
            ("🇧🇬 BGN - Bulgarian Lev", "BGN"),
            ("🇧🇷 BRL - Brazilian Real", "BRL"),
            ("🇨🇿 CZK - Czech Koruna", "CZK"),
            ("🇩🇰 DKK - Danish Krone", "DKK"),
            ("🇭🇰 HKD - Hong Kong Dollar", "HKD"),
            ("🇭🇺 HUF - Hungarian Forint", "HUF"),
            ("🇮🇳 INR - Indian Rupee", "INR"),
            ("🇮🇩 IDR - Indonesian Rupiah", "IDR"),
            ("🇮🇱 ILS - Israeli Shekel", "ILS"),
            ("🇰🇷 KRW - South Korean Won", "KRW"),
            ("🇲🇾 MYR - Malaysian Ringgit", "MYR"),
            ("🇲🇽 MXN - Mexican Peso", "MXN"),
            ("🇳🇿 NZD - New Zealand Dollar", "NZD"),
            ("🇳🇴 NOK - Norwegian Krone", "NOK"),
            ("🇵🇭 PHP - Philippine Peso", "PHP"),
            ("🇵🇱 PLN - Polish Zloty", "PLN"),
            ("🇷🇴 RON - Romanian Leu", "RON"),
            ("🇷🇺 RUB - Russian Ruble", "RUB"),
            ("🇸🇬 SGD - Singapore Dollar", "SGD"),
            ("🇿🇦 ZAR - South African Rand", "ZAR"),
            ("🇸🇪 SEK - Swedish Krona", "SEK"),
            ("🇹🇭 THB - Thai Baht", "THB"),
            ("🇹🇷 TRY - Turkish Lira", "TRY"),
            ("🇦🇪 AED - Emirati Dirham", "AED")
        ]

        # Extract display texts for combobox
        currency_display = [opt[0] for opt in self.currency_options]

        tk.Label(self.window, text="Select Currency:",
                 font=("Comic Sans MS", 11)).pack(pady=(20, 5))

        self.currency_combobox = ttk.Combobox(
            self.window,
            width=25,
            font=("Comic Sans MS", 11),
            values=currency_display,
            textvariable=self.selected_currency
        )
        self.currency_combobox.pack()
        self.currency_combobox.current(0)  # Set default to first option

        # OK button
        ok_btn = tk.Button(
            self.window,
            text="OK",
            command=self.on_ok,
            font=("Comic Sans MS", 12),
            width=10
        )
        ok_btn.pack(pady=20)

    def on_ok(self):
        # Get the selected currency code
        selected_text = self.selected_currency.get()
        currency_code = next((code for text, code in self.currency_options if text == selected_text), "USD")

        # Get the format choice
        format_choice = self.formatting_of_currency.get()
        custom_format = None

        if format_choice == "custom":
            custom_format = self.custom_format_entry.get()
            if not custom_format:
                print("Warning", "Please enter a custom format")
                return

        print(f"Currency format: {format_choice}")

        if custom_format:
            print(f"Custom format: {custom_format}")
        print(f"Selected currency: {currency_code}")

        # Here you would typically save these preferences
        self.parent.preferred_currency = currency_code
        self.parent.currency_format = custom_format if format_choice == "custom" else "0.00"

        self.parent.update_options(self.selected_currency.get(), self.formatting_of_currency.get(), custom_format)
        self.window.destroy()

    def _display_text_box(self):
        # Create frame to contain the custom format widgets
        if hasattr(self, 'custom_format_frame'):
            self.custom_format_frame.destroy()

        self.custom_format_frame = tk.Frame(self.window)
        self.custom_format_frame.pack(pady=5)

        # Label for the input field
        format_label = tk.Label(
            self.custom_format_frame,
            text="Enter custom format (e.g., 0.000, 0,000, 0#000):",
            font=("Comic Sans MS", 10)
        )
        format_label.pack(anchor=tk.W)

        # Entry field for custom format
        self.custom_format_entry = tk.Entry(
            self.custom_format_frame,
            width=20,
            font=("Comic Sans MS", 10)
        )
        self.custom_format_entry.pack(anchor=tk.W)

        # Example formats for guidance
        examples_label = tk.Label(
            self.custom_format_frame,
            text="Examples:\n0.000 → 1234.567\n0,000 → 1234,567\n0#000 → 1234#567",
            font=("Comic Sans MS", 9),
            justify=tk.LEFT
        )
        examples_label.pack(anchor=tk.W, pady=(5, 0))