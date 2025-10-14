import tkinter as tk
from tkinter import ttk

class HelpWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent.root)
        self.window.title("Quick Start Guide")
        self.window.geometry("600x500")

        self.preferred_font = parent.preferred_font
        self.preferred_size = parent.preferred_size
        
        self._setup_gui()
    
    def _setup_gui(self):
        main_frame = tk.Frame(self.window, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = tk.Label(
            main_frame, 
            text="Quick Start Guide", 
            font=(self.preferred_font, 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        help_text = """
1. SELECT COMPONENT TYPE
   - Choose the PC component you want to scrape from the dropdown (GPU, CPU, etc.)

2. SELECT WEBSITE
   - Choose which website to scrape from (Desktop.bg, Ardes.bg, etc.)

3. ENTER SEARCH TERM
   - Type the model you're looking for in the search field
   - Press Enter or click Submit

4. VIEW RESULTS
   - Results will appear in the text area below
   - Progress will be shown in the progress bar

5. EXPORT DATA
   - Results are automatically saved to Excel on your Desktop
   - Use 'Select Save Folder' to change the save location

Tips:
- You can change currency, font, and other settings in User Options
- The application supports multiple websites and currencies
- Scraping happens in the background so you can continue using the app
"""
        
        self.text_widget = tk.Text(
            main_frame, 
            wrap=tk.WORD, 
            font=(self.preferred_font, self.preferred_size),
            padx=10, 
            pady=10
        )
        self.text_widget.insert(1.0, help_text)
        self.text_widget.config(state=tk.DISABLED)  

        self.scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.text_widget.yview)
        self.text_widget.config(yscrollcommand=self.scrollbar.set)

        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.close_btn = tk.Button(
            main_frame, 
            text="Close", 
            command=self.window.destroy,
            font=(self.preferred_font, self.preferred_size)
        )
        self.close_btn.pack(pady=10)

    def update_fonts(self, font, size):
        """Update fonts in the help window"""
        self.preferred_font = font
        self.preferred_size = size
        
        try:
            if hasattr(self, 'title_label') and self.title_label.winfo_exists():
                self.title_label.config(font=(font, 16, "bold"))
            
            if hasattr(self, 'text_widget') and self.text_widget.winfo_exists():
                self.text_widget.config(font=(font, size))
            
            if hasattr(self, 'close_btn') and self.close_btn.winfo_exists():
                self.close_btn.config(font=(font, size))
                
        except Exception as e:
            print(f"Error updating HelpWindow fonts: {e}")

    def _update_widget_fonts(self, widget):
        """Recursively update fonts for all child widgets"""
        try:
            if isinstance(widget, (tk.Label, tk.Button)):
                current_font = widget.cget('font')
                if 'bold' in str(current_font):
                    widget.config(font=(self.preferred_font, self.preferred_size, "bold"))
                else:
                    widget.config(font=(self.preferred_font, self.preferred_size))
            elif isinstance(widget, tk.Text):
                widget.config(font=(self.preferred_font, self.preferred_size))

            for child in widget.winfo_children():
             self._update_widget_fonts(child)
        except:
            pass  