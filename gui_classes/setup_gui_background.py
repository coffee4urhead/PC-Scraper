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
    
    def setup_background(self):
        bg_image_path = resource_path("images/nebula-star.png")
        pil_image = Image.open(bg_image_path).convert("RGB")
        
        pil_image = pil_image.resize((1200, 700))
        blurred = pil_image.filter(ImageFilter.GaussianBlur(radius=5))

        overlay = Image.new("RGB", blurred.size, (255, 255, 255))
        self.blended_bg = Image.blend(blurred, overlay, alpha=0.2)
        
        self.master.bg_image = ctk.CTkImage(light_image=self.blended_bg, size=(1200, 700))
    
    def apply_background_to_tab(self, tab):
        bg_label = ctk.CTkLabel(tab, image=self.master.bg_image, text="")
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.tab_backgrounds.append(bg_label)