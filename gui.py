import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from scraper import AmazonGPUScraper
import pygame


class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.scraper = AmazonGPUScraper(self.update_gui)
        self.root.title("GUI App for Scraping General GPU Information")
        self.root.geometry("1200x700")

        pygame.mixer.init()
        self.music_playing = False
        self._setup_gui()
        self.root.mainloop()

    def _setup_gui(self):
        # Background image setup
        image = Image.open("./images/elf.jpg")
        resized_image = image.resize((1200, 700), Image.Resampling.LANCZOS)
        self.background_image = ImageTk.PhotoImage(resized_image)

        canvas = tk.Canvas(self.root, width=1200, height=700, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=self.background_image, anchor="nw")

        # Title label
        label1 = tk.Label(self.root, text="GPU Web Scraper Program",
                          font=("Comic Sans MS", 16, "bold"), bg='white')
        canvas.create_window(600, 50, anchor="center", window=label1)

        # Search label and entry
        label2 = tk.Label(self.root, text="Search GPU model to scrape information:",
                          font=("Comic Sans MS", 12), bg='white')
        canvas.create_window(400, 120, anchor="center", window=label2)

        self.entry = tk.Entry(self.root, width=30, font=("Comic Sans MS", 13, "italic"))
        self.root.bind("<Return>", self._on_key_press)
        canvas.create_window(750, 120, anchor="center", window=self.entry)

        # Buttons
        self.submit_button = tk.Button(self.root, text="Submit", command=self._on_submit,
                                       width=7, font=("Comic Sans MS", 13, "bold"),
                                       height=1, cursor="hand2", padx=10, pady=5)
        canvas.create_window(650, 180, anchor="center", window=self.submit_button)

        quit_button = tk.Button(self.root, text="Quit", command=self.root.destroy,
                                width=7, font=("Comic Sans MS", 13, "bold"),
                                height=1, cursor="hand2", padx=10, pady=5)
        canvas.create_window(850, 180, anchor="center", window=quit_button)

        self.play_music_button = tk.Button(self.root, text="Play Music", command=self._toggle_music,
                                           width=7, font=("Comic Sans MS", 13, "bold"),
                                           height=1, cursor="hand2", padx=10, pady=5)
        canvas.create_window(750, 180, anchor="center", window=self.play_music_button)

        # Add progress bar
        self.progress_bar = ttk.Progressbar(self.root, orient='horizontal',
                                            length=600, mode='determinate')
        canvas.create_window(600, 230, anchor="center", window=self.progress_bar)

        # Add status label
        self.status_label = tk.Label(self.root, text="Ready to scrape...",
                                     font=("Comic Sans MS", 12), bg='white', padx=7, pady=7)
        canvas.create_window(600, 260, anchor="center", window=self.status_label)

        # Add results text area with scrollbar
        results_frame = tk.Frame(self.root)
        canvas.create_window(600, 450, anchor="center", window=results_frame,
                             width=1000, height=400)

        self.results_text = tk.Text(results_frame, wrap=tk.WORD,
                                    font=("Comic Sans MS", 11),
                                    width=120, height=20)
        scrollbar = tk.Scrollbar(results_frame, command=self.results_text.yview)
        self.results_text.config(yscrollcommand=scrollbar.set)

        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure text tags for styling
        self.results_text.tag_config('error', foreground='red')

    def _toggle_music(self):
        if not self.music_playing:
            pygame.mixer.music.load("./Music/scraping-music.wav")
            pygame.mixer.music.play()
            self.play_music_button.config(text="Pause")
            self.music_playing = True
        else:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
                self.play_music_button.config(text="Resume")
            else:
                pygame.mixer.music.unpause()
                self.play_music_button.config(text="Pause")

    def update_gui(self, data):
        """Handle all updates from the scraper thread in a thread-safe manner"""
        if not data:  # Handle empty data
            return

        # Schedule the actual GUI update to run in the main thread
        self.root.after(0, self._process_scraper_update, data)

    def _process_scraper_update(self, data):
        """Process different types of updates from the scraper"""
        try:
            if data['type'] == 'progress':
                # Update progress bar and status
                self.progress_bar['value'] = data['value']
                self.status_label.config(
                    text=f"Scraping... {data['value']}% complete",
                    foreground="blue"
                )

            elif data['type'] == 'product':
                # Add product to results display
                product = data['data']
                display_text = (
                    f"GPU Found:\n"
                    f"• Title: {product['title']}\n"
                    f"• Price: {product.get('price', 'N/A')}\n"
                    f"• Page: {data.get('page', 'N/A')}\n"
                    f"{'-' * 50}\n"
                )
                self.results_text.insert(tk.END, display_text)
                self.results_text.see(tk.END)  # Auto-scroll to bottom

            elif data['type'] == 'error':
                # Show error message
                self.results_text.insert(
                    tk.END,
                    f"ERROR: {data['message']}\n\n",
                    'error'
                )
                self.status_label.config(
                    text=f"Error: {data['message']}",
                    foreground="red"
                )
                self.progress_bar['value'] = 0
                self.submit_button.config(state=tk.NORMAL)

            elif data['type'] == 'complete':
                # Final completion message
                self.status_label.config(
                    text="Scraping completed successfully!",
                    foreground="green"
                )
                self.progress_bar['value'] = 100
                self.submit_button.config(state=tk.NORMAL)

        except Exception as e:
            # Handle any errors in processing updates
            self.results_text.insert(
                tk.END,
                f"GUI Update Error: {str(e)}\n\n",
                'error'
            )
            self.status_label.config(
                text=f"Update Error: {str(e)}",
                foreground="red"
            )

    def _on_key_press(self, event):
        self._start_scraping()

    def _on_submit(self):
        self._start_scraping()

    def _start_scraping(self):
        search_term = self.entry.get().strip()
        if search_term:
            self.results_text.delete(1.0, tk.END)
            self.submit_button.config(state=tk.DISABLED)
            self.progress_bar['value'] = 0
            self.status_label.config(text="Starting scrape...", foreground="blue")
            self.scraper.start_scraping(search_term)

GUI()