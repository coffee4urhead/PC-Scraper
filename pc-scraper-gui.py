import customtkinter as ctk
from PIL import Image, ImageFilter
from gui import resource_path

class GUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PC Scraper GUI")
        self.geometry("1200x700")
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.setup_background()
        self.create_panels()

    def setup_background(self):
        """Setup the blurred background"""
        bg_image_path = resource_path("images/nebula-star.png")
        pil_image = Image.open(bg_image_path).convert("RGB")
        
        pil_image = pil_image.resize((1200, 700))
        blurred = pil_image.filter(ImageFilter.GaussianBlur(radius=5))

        overlay = Image.new("RGB", blurred.size, (255, 255, 255))
        self.blended_bg = Image.blend(blurred, overlay, alpha=0.2)
        
        self.bg_image = ctk.CTkImage(light_image=self.blended_bg, size=(1200, 700))
        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def create_panels(self):
        """Create left and right panels with visible rounded corners"""

        self.left_panel = ctk.CTkFrame(
            self, 
            width=500, 
            height=700,
            fg_color=("#FFFFFF", "#1A1A1A"),
            border_width=2,
            border_color=("#FFFFFF", "#1A1A1A"),
        )
        self.left_panel.place(x=30, y=35, relwidth=0.6, relheight=0.9)

        self.right_panel = ctk.CTkFrame(
            self, 
            width=400, 
            height=700, 
            fg_color="#1A1A1A",  
            border_width=2,
            border_color=("#FFFFFF", "#1A1A1A"),
        )
        self.right_panel.place(x=770, y=35, relwidth=0.33, relheight=0.9)

        self.add_panel_content()

    def add_panel_content(self):
        """Add some content to demonstrate the rounded corners"""
        left_title = ctk.CTkLabel(
            self.left_panel,
            text="PC Parts Web Scraper",
            text_color="white",
            font=("Arial", 20, "bold"),
            fg_color="transparent"
        )
        left_title.place(relx=0.05, rely=0.02)

        left_entry = ctk.CTkEntry(
            self.left_panel, 
            width=370, 
            height=40, 
            corner_radius=20, 
            text_color=("black", "white"),
            fg_color=("#FFFFFF", "#1A1A1A"),
            placeholder_text='Enter your desired part here ...',
            placeholder_text_color=("#666666", "#888888")
        )
        left_entry.place(relx=0.05, rely=0.1) 
        
        options = ['Ardes.bg', 'AllStore.bg', 'Amazon.co.uk', 'Hits.bg', 'Tova.bg', 'Ezona.bg', 'GtComputers.bg', 'Thx.bg', 'Senetic.bg', 'TehnikStore.bg', 'Pro.bg', 'TechnoMall.bg', 'PcTech.bg', 'CyberTrade.bg', 'Xtreme.bg', 'Optimal Computers', 'Plasico.bg', 'PIC.bg', 'jarcomputers.com', 'Desktop.bg', 'Amazon.com', 'Amazon.de']

        left_website_select = ctk.CTkComboBox(
            self.left_panel,
            width=170,  
            height=40,
            fg_color=("#FFFFFF", "#1A1A1A"),
            values=options,
            corner_radius=20,
            border_color=("#E599F0", "#592461"),  
            text_color=("black", "white"), 
            button_color=("#3B8ED0", "#1F6AA5"),  
            dropdown_fg_color=("#FFFFFF", "#1A1A1A"),  
            dropdown_text_color=("black", "white")  
        )
        left_website_select.place(relx=0.6, rely=0.1)
        
        bg_image_path = resource_path("images/Uriy1966-Steel-System-Library-Mac.64.png")
        pil_image = Image.open(bg_image_path).convert("RGB")

        ctk_image = ctk.CTkImage(
            light_image=pil_image,
            dark_image=pil_image,
            size=(30, 30),
        )

        left_select_folder_button = ctk.CTkButton(
            self.left_panel,
            width=30,
            height=40,
            corner_radius=20,
            fg_color=("#FFFFFF", "#1A1A1A"),
            border_color=("#E599F0", "#592461"),
            hover_color=("#E7E4E4", "#2E2B2B"),
            image=ctk_image,
            text=''
        )
        left_select_folder_button.place(relx=0.9, rely=0.1)

        progress_bar = ctk.CTkProgressBar(
            self.left_panel,
            width=1250,
            height=40,
            corner_radius=20,
            fg_color=("#FFFFFF", "#1A1A1A"),
            progress_color=('#B5B9EE', "#8E93E2")
        )
        progress_bar.place(relx=0.05, rely=0.2)

        left_scrape_button = ctk.CTkButton(
            self.left_panel,
            width=150,
            height=45,
            corner_radius=20,
            font=('Times New Roman', 30),
            fg_color=("#DFB6E5", "#E599F0"),
            border_color=("#E599F0", "#592461"),
            hover_color=("#DFB6E5", "#E599F0"),
            text='Scrape'
        )
        left_scrape_button.place(relx=0.4, rely=0.3)

        left_frame_label_container = ctk.CTkFrame(
            self.left_panel, 
            width=600, 
            height=400,
            fg_color=("#DBD8D8", "#232323"),
            border_width=2,
            border_color=("#FFFFFF", "#1A1A1A"),
            corner_radius=30
        )
        left_frame_label_container.place(relx=0.09, rely=0.3)

        left_label_container = ctk.CTkFrame(
            left_frame_label_container,
            fg_color="transparent"
        )
        left_label_container.pack(fill='both', expand=True, padx=100, pady=100)

        left_label_description = ctk.CTkLabel(
            left_label_container,
            text='Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industrys standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.',
            anchor='w',
            font=('Times New Roman', 20),
            justify='left',
            wraplength=450,  
        )
        left_label_description.pack(fill='both', expand=True, padx=10, pady=10)

        options_icon_path = resource_path("images/gears.png")
        gearwheel_image = Image.open(options_icon_path)
        gearwheel_image_ctk = ctk.CTkImage(light_image=gearwheel_image, dark_image=gearwheel_image, size=(40, 40))
        self.options_menu = ctk.CTkButton(
            self.left_panel,
            width=40,
            height=40,
            fg_color=("#E79CEE", "#C251CC"),
            hover_color=("#E7A2EE", "#CF55DA"),
            text='',
            image=gearwheel_image_ctk
        )
        self.options_menu.place(relx=0.9, rely=0.9)

        right_title = ctk.CTkLabel(
            self.right_panel,
            text="Console", 
            text_color="white",
            font=("Arial", 20, "bold"),
            fg_color="transparent"
        )
        right_title.place(relx=0.05, rely=0.02)

        right_console = ctk.CTkTextbox(
            self.right_panel,
            width=350,
            height=550,
            fg_color=("#FFFFFF", "#000000"),
            text_color='green',
            wrap='word',
        )
        right_console.place(relx=0.05, rely=0.1)

if __name__ == "__main__":
    app = GUI()
    app.mainloop()