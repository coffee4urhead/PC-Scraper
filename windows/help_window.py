import tkinter as tk

class HelpWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent.root)
        self.window.title("Help Documentation")
        self.window.geometry("800x600")

        # Make the help window modal (optional)
        self.window.grab_set()
        self.window.transient(parent.root)

        self._setup_ui()

    def _setup_ui(self):
        # Create a text widget for help content
        help_text = tk.Text(self.window, wrap=tk.WORD, font=("Arial", 12))
        help_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Add scrollbar
        scrollbar = tk.Scrollbar(self.window, command=help_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        help_text.config(yscrollcommand=scrollbar.set)

        # Add help content
        help_content = """Web Scraper Help Guide

1. How to Use:
- Enter your search term in the input field
- Select the PC part type from the dropdown
- Choose your preferred website
- Click Submit or press Enter to start scraping

2. Features:
- Real-time progress tracking
- Multiple website support
- Detailed product information
- Export capabilities

3. Troubleshooting:
- If scraping fails, check your internet connection
- Some websites may block automated scraping
- Try different search terms if no results appear

4. Keyboard Shortcuts:
- Enter: Start scraping
- Ctrl+Q: Quit application
"""

        help_text_gui_comp = tk.Label(help_text, text=help_content, justify=tk.CENTER, padx=20, pady=20, font=("Comic Sans MS", 12))
        help_text_gui_comp.pack()
        # Add close button
        close_btn = tk.Button(
            self.window,
            text="Close",
            command=self.window.destroy,
            font=("Comic Sans MS", 12),
            width=10
        )
        close_btn.pack(pady=10)