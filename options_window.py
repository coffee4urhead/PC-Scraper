import tkinter as tk
from tkinter import ttk

class OptionsWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent.root)
        self.window.title("User Options")
        self.window.geometry("700x850")
        self.window.configure(bg='white')
        
        self.window.transient(parent.root)
        self.window.grab_set()
        
        self.currency_options = [
            ("US Dollar (USD)", "USD"),
            ("Euro (EUR)", "EUR"), 
            ("British Pound (GBP)", "GBP"),
            ("Japanese Yen (JPY)", "JPY"),
            ("Bulgarian Lev (BGN)", "BGN"),
            ("Brazilian Real (BRL)", "BRL"),
            ("Canadian Dollar (CAD)", "CAD")
        ]
        
        self._setup_gui()
    
    def _setup_gui(self):
        main_frame = tk.Frame(self.window, bg='white', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
    
        title_label = tk.Label(
            main_frame, 
            text="User Preferences", 
            font=("Arial", 16, "bold"),
            bg='white'
        )
        title_label.pack(pady=(0, 20))

        ###
        font_frame = tk.LabelFrame(
            main_frame, 
            text="Font Settings", 
            font=("Arial", 12, "bold"),
            bg='white',
            padx=10,
            pady=10
        )

        tk.Label(
            font_frame,
            text="Font Family:",
            font=("Arial", 10),
            bg='white'
        ).pack(anchor='w', pady=(0, 5))

        self.font_family_combobox = ttk.Combobox(
            font_frame,
            values=["Arial", "Courier New", "Georgia", "Times New Roman", "Verdana"],
            state="readonly",
            font=("Arial", 10),
            width=30
        )
        self.font_family_combobox.pack(fill=tk.X, pady=(0, 10))
        # Set default value using set() method
        current_font = getattr(self.parent, 'preferred_font', 'Arial')
        self.font_family_combobox.set(current_font)

        tk.Label(
            font_frame,
            text="Font Size:",
            font=("Arial", 10),
            bg='white'
        ).pack(anchor='w', pady=(0, 5))

        self.font_size_combobox = ttk.Combobox(
            font_frame,
            values=[str(i) for i in range(8, 25)],
            state="readonly",
            font=("Arial", 10),
            width=30
        )
        self.font_size_combobox.pack(fill=tk.X, pady=(0, 10))
        # Set default value using set() method
        current_size = str(getattr(self.parent, 'preferred_size', 12))
        self.font_size_combobox.set(current_size)

        font_frame.pack(fill=tk.X, pady=(0, 15))

        currency_frame = tk.LabelFrame(
            main_frame, 
            text="Currency Settings", 
            font=("Arial", 12, "bold"),
            bg='white',
            padx=10,
            pady=10
        )
        currency_frame.pack(fill=tk.X, pady=(0, 15))
    
        tk.Label(
            currency_frame, 
            text="Preferred Currency:",
            font=("Arial", 10),
            bg='white'
        ).pack(anchor='w', pady=(0, 5))
    
        self.currency_combobox = ttk.Combobox(
            currency_frame,
            values=[opt[0] for opt in self.currency_options],
            state="readonly",
            font=("Arial", 10),
            width=30
        )
        self.currency_combobox.pack(fill=tk.X, pady=(0, 10))
    
        # Set default currency
        current_currency_text = next(
            (text for text, code in self.currency_options if code == self.parent.preferred_currency),
            "Bulgarian Lev (BGN)"
        )
        self.currency_combobox.set(current_currency_text)

        format_frame = tk.LabelFrame(
            main_frame, 
            text="Price Format", 
            font=("Arial", 12, "bold"),
            bg='white',
            padx=10,
            pady=10
        )
        format_frame.pack(fill=tk.X, pady=(0, 15))

        self.format_var = tk.StringVar(value="standard")
    
        ttk.Radiobutton(
            format_frame,
            text="Standard Format (0.00)",
            variable=self.format_var,
            value="standard"
        ).pack(anchor='w', pady=2)
    
        ttk.Radiobutton(
            format_frame,
            text="No Decimal Places (0)",
            variable=self.format_var,
            value="no_decimal"
        ).pack(anchor='w', pady=2)
    
        ttk.Radiobutton(
            format_frame,
            text="Custom Format",
            variable=self.format_var,
            value="custom"
        ).pack(anchor='w', pady=2)
    
        self.custom_format_frame = tk.Frame(format_frame, bg='white')
        self.custom_format_frame.pack(fill=tk.X, pady=(5, 0))

        tk.Label(
            self.custom_format_frame,
            text="Custom Format:",
            font=("Arial", 9),
            bg='white'
        ).pack(side=tk.LEFT, padx=(20, 5))
    
        self.custom_format_entry = ttk.Entry(
        self.custom_format_frame,
        width=15,
        font=("Arial", 9)
        )
        self.custom_format_entry.pack(side=tk.LEFT)
        self.custom_format_entry.insert(0, "0.000")  
    
        self.format_var.trace('w', self._on_format_change)
        self._on_format_change()
    
        browser_frame = tk.LabelFrame(
            main_frame, 
            text="Default Browser", 
            font=("Arial", 12, "bold"),
            bg='white',
            padx=10,
            pady=10
        )
        browser_frame.pack(fill=tk.X, pady=(0, 15))
    
        tk.Label(
            browser_frame, 
            text="Default Web Browser:",
            font=("Arial", 10),
            bg='white'
        ).pack(anchor='w', pady=(0, 5))
    
        browser_options = [
        "Chrome", 
            "Firefox", 
            "Edge", 
            "Safari",
            "Opera",
            "Brave"
        ]
    
        self.browser_combobox = ttk.Combobox(
            browser_frame,
            values=browser_options,
            state="readonly",
            font=("Arial", 10),
            width=30
        )
        self.browser_combobox.pack(fill=tk.X, pady=(0, 10))
        # Set default browser
        current_browser = getattr(self.parent, 'preferred_browser', 'Chrome')
        self.browser_combobox.set(current_browser)
    
        theme_frame = tk.LabelFrame(
            main_frame, 
            text="Application Theme", 
            font=("Arial", 12, "bold"),
            bg='white',
            padx=10,
            pady=10
        )
        theme_frame.pack(fill=tk.X, pady=(0, 20))
    
        tk.Label(
         theme_frame, 
         text="UI Theme:",
         font=("Arial", 10),
         bg='white'
        ).pack(anchor='w', pady=(0, 5))
    
        theme_options = [
            "Light",
            "Dark", 
            "System Default",
            "Blue Theme",
            "Green Theme"
        ]
    
        self.theme_combobox = ttk.Combobox(
            theme_frame,
            values=theme_options,
            state="readonly",
            font=("Arial", 10),
            width=30
        )
        self.theme_combobox.pack(fill=tk.X, pady=(0, 10))
        # Set default theme
        current_theme = getattr(self.parent, 'preferred_theme', 'Light')
        self.theme_combobox.set(current_theme)
    
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill=tk.X, pady=(10, 0))

        apply_btn = ttk.Button(
            button_frame,
            text="Apply Settings",
            command=self._apply_settings
        )
        apply_btn.pack(side=tk.RIGHT, padx=(10, 0))
    
        cancel_btn = ttk.Button(
            button_frame,
            text="Cancel",
            command=self.window.destroy
        )
        cancel_btn.pack(side=tk.RIGHT)
    
        reset_btn = ttk.Button(
            button_frame,
            text="Reset to Defaults",
            command=self._reset_to_defaults
        )
        reset_btn.pack(side=tk.LEFT)
    
    def _on_format_change(self, *args):
        """Show/hide custom format entry based on selection"""
        if self.format_var.get() == "custom":
            self.custom_format_entry.config(state='normal')
        else:
            self.custom_format_entry.config(state='disabled')
    
    def _apply_settings(self):
        """Apply all selected settings"""
        try:
            selected_text = self.currency_combobox.get()
            currency_code = next(
                    (code for text, code in self.currency_options if text == selected_text),
            "BGN"
            )
            selected_font = self.font_family_combobox.get()
            selected_size = int(self.font_size_combobox.get())
        
            print(f"Font set to: {selected_font}, Size: {selected_size}")

            format_choice = self.format_var.get()
            custom_format = self.custom_format_entry.get() if format_choice == "custom" else None
        
            selected_browser = self.browser_combobox.get()
            selected_theme = self.theme_combobox.get()
        
            # Update parent with ALL settings including font preferences
            self.parent.update_options(selected_text, format_choice, custom_format, selected_browser, selected_theme)
        
            # Update font preferences in parent
            self.parent.preferred_font = selected_font
            self.parent.preferred_size = selected_size
        
            # CALL THE UPDATE FONTS METHOD HERE
            if hasattr(self.parent, 'update_fonts'):
                self.parent.update_fonts()
                print("Fonts updated successfully")
            else:
                print("Warning: update_fonts method not found in parent")
        
            if hasattr(self.parent, 'update_browser_preference'):
                self.parent.update_browser_preference(selected_browser)
            else:
                self.parent.preferred_browser = selected_browser
                print(f"Default browser set to: {selected_browser}")
        
            if hasattr(self.parent, 'update_theme_preference'):
                self.parent.update_theme_preference(selected_theme)
            else:
                self.parent.preferred_theme = selected_theme
                print(f"UI theme set to: {selected_theme}")
        
            self._show_success_message()
        
        except Exception as e:
            print(f"Error applying settings: {e}")
    
    def _reset_to_defaults(self):
        """Reset all settings to default values"""
        self.currency_combobox.set("Bulgarian Lev (BGN)")
        self.format_var.set("standard")
        self.custom_format_entry.delete(0, tk.END)
        self.custom_format_entry.insert(0, "0.000")
        self.browser_combobox.set("Chrome")
        self.theme_combobox.set("Light")
        self.font_family_combobox.set("Arial")
        self.font_size_combobox.set("12")
    
    def _show_success_message(self):
        """Show success message and close window"""
        success_window = tk.Toplevel(self.window)
        success_window.title("Success")
        success_window.geometry("300x100")
        success_window.transient(self.window)
        success_window.grab_set()
        
        tk.Label(
            success_window, 
            text="Settings applied successfully!",
            font=("Arial", 11),
            pady=20
        ).pack()
        
        ttk.Button(
            success_window,
            text="OK",
            command=lambda: [success_window.destroy(), self.window.destroy()]
        ).pack(pady=5)