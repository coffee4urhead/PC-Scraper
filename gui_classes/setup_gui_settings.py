import customtkinter as ctk
from tkinter import colorchooser
import json
import os

class SettingsTabSetup:
    def __init__(self, master, settings_manager):
        self.master = master
        self.settings_manager = settings_manager
    
    def update_font_family(self, selected_font):
        """Update font family setting"""
        print(f"Updating font family to: {selected_font}")
        self.master.preferred_font = selected_font
        self.settings_manager.set_ui_setting('preferred_font', selected_font)
        
        if hasattr(self.master, 'setup_gui_instance'):
            self.master.setup_gui_instance.refresh_gui()
        else:
            print("ERROR: setup_gui_instance not found on master")
    
    def update_font_size(self, selected_size):
        """Update font size setting"""
        print(f"Updating font size to: {selected_size}")
        self.master.preferred_size = int(selected_size)
        self.settings_manager.set_ui_setting('preferred_size', selected_size)
        
        if hasattr(self.master, 'setup_gui_instance'):
            self.master.setup_gui_instance.refresh_gui()
        else:
            print("ERROR: setup_gui_instance not found on master")
    
    def update_language(self, selected_language):
        """Update language setting"""
        print(f"Updating language to: {selected_language}")
        self.master.preferred_language = selected_language
        self.settings_manager.set_ui_setting('preferred_language', selected_language)
        
        if hasattr(self.master, 'setup_gui_instance'):
            self.master.setup_gui_instance.refresh_gui()
        else:
            print("ERROR: setup_gui_instance not found on master")

    def setup_settings_tab(self, tab):
        self._setup_look_and_feel_panel(tab)
        self._setup_font_settings(tab)
        self._setup_color_customization(tab)
    
    def _setup_look_and_feel_panel(self, tab):
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
    
    def _setup_font_settings(self, tab):
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

        font_family_label = ctk.CTkLabel(
            font_frame,
            text="Font Family", 
            text_color="white",
            font=(self.master.preferred_font, 15, "bold"),
            fg_color="transparent"
        )
        font_family_label.place(relx=0.1, rely=0.1)
        
        font_family_options = [
            "Arial", "Helvetica", "Times New Roman", "Courier New",
            "Verdana", "Georgia", "Tahoma", "Trebuchet MS",
            "Comic Sans MS", "Impact", "Lucida Console", "Lucida Sans Unicode",
            "Palatino Linotype", "Garamond", "Bookman Old Style", "Arial Black",
            "Symbol", "Wingdings", "MS Sans Serif", "MS Serif", "Segoe UI",
            "Calibri", "Cambria", "Candara", "Consolas", "Constantia", "Corbel",
            "Franklin Gothic Medium", "Geneva", "Courier", "Monaco", "Andale Mono",
            "Monospace", "Sans-serif", "Serif"
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
            state='readonly',
            command=self.update_font_family,
            font=(self.master.preferred_font, 15)
        )
        self.font_family_select.set(self.master.preferred_font)
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
            "af-ZA", "ar-SA", "bg-BG", "ca-ES", "cs-CZ", "da-DK", "de-DE", "el-GR",
            "en-US", "en-GB", "es-ES", "es-MX", "et-EE", "fi-FI", "fr-FR", "he-IL",
            "hi-IN", "hr-HR", "hu-HU", "id-ID", "it-IT", "ja-JP", "ko-KR", "lt-LT",
            "lv-LV", "nb-NO", "nl-NL", "pl-PL", "pt-BR", "pt-PT", "ro-RO", "ru-RU",
            "sk-SK", "sl-SI", "sr-RS", "sv-SE", "th-TH", "tr-TR", "uk-UA", "vi-VN",
            "zh-CN", "zh-TW"
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
            font=(self.master.preferred_font, 15)
        )
        self.language_select.set(self.master.preferred_language)
        self.language_select.place(relx=0.4, rely=0.35)
        
        font_size_label = ctk.CTkLabel(
            font_frame,
            text="Font Size", 
            text_color="white",
            font=(self.master.preferred_font, 15, "bold"),
            fg_color="transparent"
        )
        font_size_label.place(relx=0.1, rely=0.7)
        
        font_size_options = [str(i) for i in range(8, 21)]  
        
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
            font=(self.master.preferred_font, 15)
        )
        self.font_size_select.set(str(self.master.preferred_size))
        self.font_size_select.place(relx=0.4, rely=0.65)
    
    def _setup_color_customization(self, tab):
        """Setup color customization section"""
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
    
    def setup_ui_colors_customization(self):
        """Setup the color customization UI"""
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
            fg_color=self.master.primary_color,
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
            font=(self.master.preferred_font, self.master.preferred_size),
            fg_color="transparent"
        )
        secondary_color_label.grid(row=1, column=0, sticky="w", padx=(0, 20), pady=(10, 0))
        
        self.secondary_color_display = ctk.CTkFrame(
            color_picker_frame,
            width=40,
            height=40,
            fg_color=self.master.secondary_color,
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
    
    def change_theme(self, theme):
        """Change application theme"""
        if hasattr(self.master, 'change_theme'):
            self.master.change_theme(theme)
            self.master.refresh_gui()
        else:
            print(f"Theme changed to: {theme}")
    
    def pick_primary_color(self):
        """Pick primary color"""
        color = colorchooser.askcolor(title="Choose primary color")[1]
        if color:
            self.master.primary_color = color
            self.settings_manager.set_ui_setting('primary_color', color)
            self.primary_color_display.configure(fg_color=color)
            if hasattr(self.master, 'apply_custom_colors'):
                self.master.apply_custom_colors()
    
    def pick_secondary_color(self):
        """Pick secondary color"""
        color = colorchooser.askcolor(title="Choose secondary color")[1]
        if color:
            self.master.secondary_color = color
            self.settings_manager.set_ui_setting('secondary_color', color)
            self.secondary_color_display.configure(fg_color=color)
            if hasattr(self.master, 'apply_custom_colors'):
                self.master.apply_custom_colors()
    
    def apply_preset_colors(self, primary, secondary):
        """Apply preset color combination"""
        self.master.primary_color = primary
        self.master.secondary_color = secondary
        self.settings_manager.set_ui_setting('primary_color', primary)
        self.settings_manager.set_ui_setting('secondary_color', secondary)
        self.primary_color_display.configure(fg_color=primary)
        self.secondary_color_display.configure(fg_color=secondary)
        if hasattr(self.master, 'apply_custom_colors'):
            self.master.apply_custom_colors()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        if hasattr(self.master, 'reset_to_defaults'):
            self.master.reset_to_defaults()
        else:
            print("Reset to defaults clicked")