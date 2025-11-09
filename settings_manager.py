import json
import os
from customtkinter import ThemeManager

class SettingsManager:
    def __init__(self, settings_file="scraper_settings.json"):

        self.config_dir = "configs"
        os.makedirs(self.config_dir, exist_ok=True)
        
        self.settings_file = os.path.join(self.config_dir, settings_file)
        self.theme_file = os.path.join(self.config_dir, "custom_theme.json")
        
        self.default_settings = {
            "preferred_currency": "BGN",
            "price_format": "0.00",
            "preferred_browser": "Chrome",
            "headless": False,
            "max_pages": 10,
            "delay_between_requests": 2.0,
            "random_delay_multiplier": 1.5,
            "min_price": "",
            "max_price": "",
            "exclude_keywords": "",
            "output_format": "JSON",
            "debug_logs": False,
            "auto_close": True,
            "ui_settings": {
                "preferred_font": "Verdana",
                "preferred_size": 15,
                "preferred_theme": "System",
                "preferred_language": "en-US",
                "primary_color": "#3B8ED0",
                "secondary_color": "#1F6AA5",
                "save_folder": os.path.join(os.path.expanduser("~"), "Desktop")
            }
        }
        self.settings = self.load_settings()
        self.create_default_theme()
    
    def load_settings(self):
        """Load settings from JSON file or create default if not exists"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    settings = self.default_settings.copy()
                    settings.update(loaded_settings)
                    if 'ui_settings' in loaded_settings:
                        settings['ui_settings'].update(loaded_settings['ui_settings'])
                    return settings
            else:
                self.save_settings(self.default_settings)
                return self.default_settings.copy()
        except Exception as e:
            print(f"Error loading settings: {e}")
            return self.default_settings.copy()
    
    def load_or_create_theme(self):
        """Load existing theme or create default theme"""
        if not os.path.exists(self.theme_file):
            self.create_default_theme()
    
    def create_default_theme(self):
        """Create default theme based on current UI settings"""
        primary_color = self.get_ui_setting('primary_color', '#3B8ED0')
        secondary_color = self.get_ui_setting('secondary_color', '#1F6AA5')
    
        theme_data = {
        "CTk": {
            "fg_color": ["#DCE4EE", "#1B1B1B"],
            "top_fg_color": ["#DCE4EE", "#1B1B1B"],
            "text_color": ["#000000", "#FFFFFF"]
        },
        "CTkFont": {
            "family": "Microsoft Sans Serif",
            "size": 13,
            "weight": "normal",
            "slant": "roman",
            "underline": 0,
            "overstrike": 0
        },
        "CTkButton": {
            "corner_radius": 8,
            "border_width": 0,
            "fg_color": [primary_color, primary_color],
            "hover_color": [secondary_color, secondary_color],
            "text_color": ["#FFFFFF", "#FFFFFF"],
            "text_color_disabled": ["#A0A0A0", "#808080"],
            "border_color": ["#3E454A", "#949A9F"]
        },
        "CTkFrame": {
            "corner_radius": 8,
            "border_width": 1,
            "fg_color": ["#F0F0F0", "#2B2B2B"],
            "top_fg_color": ["#F0F0F0", "#2B2B2B"],
            "border_color": [primary_color, primary_color]
        },
        "CTkEntry": {
            "corner_radius": 6,
            "border_width": 1,
            "fg_color": ["#FFFFFF", "#1E1E1E"],
            "border_color": [primary_color, primary_color],
            "text_color": ["#000000", "#FFFFFF"],
            "placeholder_text_color": ["#A0A0A0", "#808080"]
        },
        "CTkProgressBar": {
            "corner_radius": 4,
            "border_width": 0,
            "fg_color": ["#E0E0E0", "#404040"],
            "progress_color": [secondary_color, secondary_color],
            "border_color": ["#E0E0E0", "#404040"]
        },
        "CTkComboBox": {
            "corner_radius": 6,
            "border_width": 1,
            "fg_color": ["#FFFFFF", "#1E1E1E"],
            "button_color": [primary_color, primary_color],
            "button_hover_color": [secondary_color, secondary_color],
            "text_color": ["#000000", "#FFFFFF"],
            "text_color_disabled": ["#A0A0A0", "#808080"],  
            "border_color": [primary_color, primary_color]
        },
        "CTkSegmentedButton": {
            "corner_radius": 6,
            "border_width": 1,
            "fg_color": ["#F0F0F0", "#2B2B2B"],
            "selected_color": [primary_color, primary_color],
            "selected_hover_color": [secondary_color, secondary_color],
            "unselected_color": ["#E0E0E0", "#404040"],
            "unselected_hover_color": ["#D0D0D0", "#505050"],
            "text_color": ["#000000", "#FFFFFF"],
            "text_color_disabled": ["#A0A0A0", "#808080"]
        },
        "DropdownMenu": {
            "fg_color": ["#FFFFFF", "#1E1E1E"],
            "hover_color": ["#E5E5E5", "#2A2A2A"],
            "border_color": ["#CCCCCC", "#444444"],
            "text_color": ["#000000", "#FFFFFF"],
            "text_color_disabled": ["#A0A0A0", "#808080"],
            "corner_radius": 6,
            "border_width": 1
        },
        "CTkLabel": {
            "fg_color": "transparent",
            "text_color": ["#000000", "#FFFFFF"],
            "corner_radius": 0,
            "text_color_disabled": ["#A0A0A0", "#808080"]
        },
        "CTkSwitch": {
            "fg_color": ["#C0C0C0", "#606060"],
            "progress_color": [primary_color, primary_color],
            "button_color": ["#FFFFFF", "#E0E0E0"],
            "button_hover_color": ["#F0F0F0", "#D0D0D0"],
            "text_color": ["#000000", "#FFFFFF"],
            "text_color_disabled": ["#A0A0A0", "#808080"]
        },
        "CTkSlider": {
            "fg_color": ["#C0C0C0", "#606060"],
            "progress_color": [primary_color, primary_color],
            "button_color": ["#FFFFFF", "#E0E0E0"],
            "button_hover_color": ["#F0F0F0", "#D0D0D0"],
            "border_color": ["#C0C0C0", "#606060"]
        },
        "CTkOptionMenu": {
            "corner_radius": 6,
            "border_width": 1,
            "fg_color": ["#FFFFFF", "#1E1E1E"],
            "button_color": [primary_color, primary_color],
            "button_hover_color": [secondary_color, secondary_color],
            "text_color": ["#000000", "#FFFFFF"],
            "border_color": [primary_color, primary_color]
        },
        "CTkScrollableFrame": {
            "corner_radius": 8,
            "border_width": 1,
            "fg_color": ["#F0F0F0", "#2B2B2B"],
            "border_color": [primary_color, primary_color],
            "scrollbar_fg_color": ["#E0E0E0", "#404040"],
            "scrollbar_button_color": [primary_color, primary_color],
            "scrollbar_button_hover_color": [secondary_color, secondary_color]
        },
        "CTkTextbox": {
            "corner_radius": 6,
            "border_width": 1,
            "fg_color": ["#FFFFFF", "#1E1E1E"],
            "border_color": [primary_color, primary_color],
            "text_color": ["#000000", "#FFFFFF"],
            "scrollbar_fg_color": ["#E0E0E0", "#404040"],
            "scrollbar_button_color": [primary_color, primary_color],
            "scrollbar_button_hover_color": [secondary_color, secondary_color]
        },
        "CTkTabview": {
            "corner_radius": 8,
            "border_width": 1,
            "fg_color": ["#F0F0F0", "#2B2B2B"],
            "border_color": [primary_color, primary_color],
            "segmented_button_fg_color": ["#F0F0F0", "#2B2B2B"],
            "segmented_button_selected_color": [primary_color, primary_color],
            "segmented_button_selected_hover_color": [secondary_color, secondary_color],
            "segmented_button_unselected_color": ["#E0E0E0", "#404040"],
            "segmented_button_unselected_hover_color": ["#D0D0D0", "#505050"],
            "text_color": ["#000000", "#FFFFFF"],
            "text_color_disabled": ["#A0A0A0", "#808080"]
        },
        "CTkScrollbar": {
            "corner_radius": 5,
            "border_spacing": 2,
            "fg_color": ["#E0E0E0", "#404040"],
            "button_color": [primary_color, primary_color],
            "button_hover_color": [secondary_color, secondary_color]
        },
    }
        try:
            with open(self.theme_file, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=4, ensure_ascii=False)
            print(f"Default theme created at {self.theme_file}")
        except Exception as e:
            print(f"Error creating default theme: {e}")
    
    def update_theme(self):
        """Update theme file when colors change"""
        self.create_default_theme()
    
    def save_settings(self, settings=None):
        """Save settings to JSON file"""
        try:
            if settings is None:
                settings = self.settings
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            print(f"Settings saved to {self.settings_file}")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set a setting value and save immediately"""
        self.settings[key] = value
        self.save_settings()
    
    def get_ui_setting(self, key, default=None):
        """Get a UI setting value"""
        return self.settings['ui_settings'].get(key, default)
    
    def set_ui_setting(self, key, value):
        """Set a UI setting value and save immediately"""
        self.settings['ui_settings'][key] = value
        self.save_settings()
        if key in ['primary_color', 'secondary_color']:
            self.update_theme()
    
    def apply_to_scraper(self, scraper):
        """Apply scraper settings to a scraper instance"""
        scraper_settings = {k: v for k, v in self.settings.items() if k != 'ui_settings'}
        for key, value in scraper_settings.items():
            setattr(scraper, key, value)
    
    def get_config_directory(self):
        """Get the config directory path"""
        return self.config_dir
    
    def get_theme_path(self):
        """Get the theme file path"""
        return self.theme_file