from PIL import Image, ImageFilter
import customtkinter as ctk
import os
import sys

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class BackgroundSetup:
    def __init__(self, master):
        self.master = master
        self.tab_backgrounds = []
        self.original_image = None
        self.current_size = (1200, 700)

    def setup_background(self):
        bg_image_path = resource_path("images/nebula-star.png")
        self.original_image = Image.open(bg_image_path).convert("RGB")
        
        self.original_image = self.original_image.resize((1200, 700))
        blurred = self.original_image.filter(ImageFilter.GaussianBlur(radius=5))

        overlay = Image.new("RGB", blurred.size, (255, 255, 255))
        self.blended_bg = Image.blend(blurred, overlay, alpha=0.2)
        
        self.master.bg_image = ctk.CTkImage(light_image=self.blended_bg, size=(1200, 700))
        self.master.bind("<Configure>", self.on_window_resize)
    
    def update_background_size(self, size):
        """Resize and blur image to new dimensions"""
        resized = self.original_image.resize(size, Image.Resampling.LANCZOS)
        blurred = resized.filter(ImageFilter.GaussianBlur(radius=5))
        
        overlay = Image.new("RGB", blurred.size, (255, 255, 255))
        self.blended_bg = Image.blend(blurred, overlay, alpha=0.2)
        
        self.master.bg_image = ctk.CTkImage(
            light_image=self.blended_bg, 
            size=size
        )
        
        for bg_label in self.tab_backgrounds:
            bg_label.configure(image=self.master.bg_image)
    
    def on_window_resize(self, event):
        """Handle window resize events"""
        if event.widget == self.master:
            new_width = event.width
            new_height = event.height
            
            if (new_width, new_height) != self.current_size and new_width > 100 and new_height > 100:
                self.current_size = (new_width, new_height)
                self.update_background_size((new_width, new_height))
    
    def apply_background_to_tab(self, tab):
        """Apply background to a tab"""
        bg_label = ctk.CTkLabel(
            tab, 
            image=self.master.bg_image, 
            text=""
        )
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        tab.bind("<Configure>", lambda e: self.on_tab_resize(e, bg_label))
        
        self.tab_backgrounds.append(bg_label)
    
    def on_tab_resize(self, event, bg_label):
        """Handle tab resize events"""
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)