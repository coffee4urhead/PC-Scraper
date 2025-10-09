import tkinter as tk
from tkinter import ttk


class WindowsFontOptions:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent.root)
        self.window.title("Language & Font Options")
        self.window.geometry("800x600")

        self.preferred_language = tk.StringVar(value='en-US')
        self.preferred_size = tk.IntVar(value=12)
        self.preferred_font = tk.StringVar(value='Comic Sans MS')

        # Make the help window modal (optional)
        self.window.grab_set()
        self.window.transient(parent.root)

        self._setup_ui()

    def _setup_ui(self):
        self.languages = [
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
        tk.Label(self.window, text="Select language:",
                 font=("Comic Sans MS", 11)).pack(pady=(20, 5))

        self.language_combobox = ttk.Combobox(
            self.window,
            width=25,
            font=("Comic Sans MS", 11),
            values=self.languages,
            textvariable=self.preferred_language
        )
        self.language_combobox.pack()
        self.language_combobox.current(0)

        self.parent.root.bind("<Return>", self._on_key_press)

        self.available_fonts = [
                "Arial",
                "Helvetica",
                "Times New Roman",
                "Courier New",
                "Comic Sans MS",
                "Verdana",
                "Georgia",
                "Trebuchet MS",
                "Lucida Console",
                "Tahoma",
                "Calibri",
                "Segoe UI",
                "Impact",
                "Palatino Linotype",
                "Garamond"
        ]

        self.font_combobox = ttk.Combobox(
            self.window,
            width=25,
            font=("Comic Sans MS", 11),
            values=self.available_fonts,
            textvariable=self.preferred_font
        )
        self.font_combobox.pack()
        self.font_combobox.current(0)

        results_frame = tk.Frame(self.parent.root)
        results_frame.pack(pady=(30, 5))

        tk.Label(self.window, text="Select font style and size ------",
                 font=("Comic Sans MS", 11)).pack(pady=(20, 5))

        tk.Label(self.window, text="Select font size:",
                 font=("Comic Sans MS", 11)).pack(pady=(30, 5))

        # Font Size Entry
        tk.Label(self.window, text="Enter font size:", font=("Comic Sans MS", 11)).pack(pady=(20, 5))
        self.font_size_entry = tk.Entry(self.window, textvariable=self.preferred_size, font=("Comic Sans MS", 11),
                                        width=10)
        self.font_size_entry.pack()

        # Font Combobox
        self.font_combobox.bind("<<ComboboxSelected>>", self.update_preview)
        self.font_size_entry.bind("<Return>", self.update_preview)

        # Preview Text
        self.preview_label = tk.Label(
            self.window,
            text="Sample text preview",
            font=(self.preferred_font.get(), self.preferred_size.get())
        )
        self.preview_label.pack(pady=(40, 10))
        ok_btn = tk.Button(
            self.window,
            text="OK",
            command=self.on_ok,
            font=("Comic Sans MS", 12),
            width=10
        )
        ok_btn.pack(pady=43)

    def on_ok(self):
        preferred_font = self.preferred_font.get()
        prefered_size = self.preferred_size.get()
        preferred_language = self.preferred_language.get()

        print(f"Language: {preferred_language}")
        print(f"Selected font: {preferred_font}")#
        print(f"Selected size: {prefered_size}")

        # Here you would typically save these preferences
        self.parent.update_language_and_font_options(preferred_font, prefered_size, preferred_language)
        self.window.destroy()

    def _on_key_press(self):
        pass

    def update_preview(self, event=None):
        try:
            font_family = self.preferred_font.get()
            font_size = int(self.preferred_size.get())
            self.preview_label.config(font=(font_family, font_size))
        except ValueError:
            # Optional: handle invalid size entry
            self.preview_label.config(text="Please enter a valid number for size")
