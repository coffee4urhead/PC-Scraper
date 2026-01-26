import customtkinter as ctk
import os
import sys
from PIL import Image

class ContentSetup:
    def __init__(self, master, settings_manager):
        self.master = master
        self.settings_manager = settings_manager
        self.part_options = ["Motherboard", 'PSU', 'RAM', 'GPU', 'Case', 'Fans', 
                           'CPU', 'AIO', 'Air Coolers', 'Extension Cables', 
                           'HDD', 'SATA SSD', 'NVME SSD']
        self.website_options = ['Ardes.bg', 'AllStore.bg', 'Amazon.co.uk', 'Hits.bg', 
                              'Tova.bg', 'Ezona.bg', 'GtComputers.bg', 'Thx.bg', 
                              'Senetic.bg', 'TehnikStore.bg', 'Pro.bg', 
                              'TechnoMall.bg', 'PcTech.bg', 'CyberTrade.bg', 
                              'Xtreme.bg', 'Optimal Computers', 'Plasico.bg', 
                              'PIC.bg', 'jarcomputers.com', 'Desktop.bg', 
                              'Amazon.com', 'Amazon.de']
        self.selected = []
        
    def _add_action_buttons(self):
        """Add action buttons to the left panel"""
        def resource_path(relative_path): 
            if hasattr(sys, '_MEIPASS'):
                base_path = sys._MEIPASS
            else: 
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)
        
        search_icon_path = resource_path("images/search.png")
        try:
            search_pil_image = Image.open(search_icon_path)
            search_ctk_image = ctk.CTkImage(
                light_image=search_pil_image,
                dark_image=search_pil_image,
                size=(30, 30),
            )
        except:
            search_ctk_image = None
        
        self.master.left_scrape_button = ctk.CTkButton(
            self.master.left_panel,
            width=40,
            height=40,
            corner_radius=20,
            font=(self.master.preferred_font, 30),
            image=search_ctk_image,
            text='' if search_ctk_image else 'Search',
            command=self._get_scrape_callback()
        )
        self.master.left_scrape_button.place(relx=0.48, rely=0.1)
        
        folder_icon_path = resource_path("images/Uriy1966-Steel-System-Library-Mac.64.png")
        try:
            folder_pil_image = Image.open(folder_icon_path)
            folder_ctk_image = ctk.CTkImage(
                light_image=folder_pil_image,
                dark_image=folder_pil_image,
                size=(30, 30),
            )
        except:
            folder_ctk_image = None
        
        self.master.left_select_folder_button = ctk.CTkButton(
            self.master.left_panel,
            width=40,
            height=40,
            corner_radius=10,
            fg_color=("#FFFFFF", "#454345"),
            hover_color=("#CBC7C7", "#2E2C2E"),
            image=folder_ctk_image,
            text='' if folder_ctk_image else 'Folder',
            command=self._get_folder_callback()
        )
        self.master.left_select_folder_button.place(relx=0.9, rely=0.1)
        
        options_icon_path = resource_path("images/gears.png")
        try:
            gearwheel_image = Image.open(options_icon_path)
            gearwheel_image_ctk = ctk.CTkImage(
                light_image=gearwheel_image, 
                dark_image=gearwheel_image, 
                size=(40, 40)
            )
        except:
            gearwheel_image_ctk = None
        
        self.master.options_menu = ctk.CTkButton(
            self.master.left_panel,
            width=40,
            height=40,
            fg_color=("#E79CEE", "#C251CC"),
            hover_color=("#E7A2EE", "#CF55DA"),
            text='' if gearwheel_image_ctk else 'Options',
            image=gearwheel_image_ctk,
            command=self._get_options_callback()
        )
        self.master.options_menu.place(relx=0.9, rely=0.9)
        
        audio_icon_path_off = resource_path("images/no-sound.png")
        audio_icon_path_on = resource_path("images/sound.png")
        
        try:
            audio_image_off = Image.open(audio_icon_path_off)
            self.audio_image_ctk_off = ctk.CTkImage(
                light_image=audio_image_off, 
                dark_image=audio_image_off, 
                size=(40, 40)
            )
            audio_image_on = Image.open(audio_icon_path_on)
            self.audio_image_ctk_on = ctk.CTkImage(
                light_image=audio_image_on, 
                dark_image=audio_image_on, 
                size=(40, 40)
            )
        except Exception as e:
            print(f"Error loading audio icons: {e}")
            self.audio_image_ctk_off = None
            self.audio_image_ctk_on = None
        
        self.mute_audio_btn = ctk.CTkButton(
            self.master.left_panel,
            width=40,
            height=40,
            fg_color=("#E79CEE", "#C251CC"),
            hover_color=("#E7A2EE", "#CF55DA"),
            text='' if self.audio_image_ctk_off else 'Music',
            image=self.audio_image_ctk_off,
            command=self._get_audio_callback()
        )
        self.mute_audio_btn.place(relx=0.8, rely=0.9)
    
    def _get_scrape_callback(self):
        """Get the scrape button callback"""
        if hasattr(self.master, '_start_scraping'):
            return self.master._start_scraping
        elif hasattr(self.master, 'start_scraping'):
            return self.master.start_scraping
        else:
            def default_callback():
                print("Scrape button clicked")
            return default_callback
    
    def _get_folder_callback(self):
        """Get the folder button callback"""
        if hasattr(self.master, 'ask_save_dir'):
            return self.master.ask_save_dir
        else:
            def default_callback():
                print("Folder button clicked")
            return default_callback
    
    def _get_options_callback(self):
        """Get the options button callback"""
        if hasattr(self.master, 'get_scraper_windows_options'):
            return self.master.get_scraper_windows_options
        else:
            def default_callback():
                print("Options button clicked")
            return default_callback
    
    def _get_audio_callback(self):
        """Get the audio button callback"""
        def toggle_audio():
            if hasattr(self, 'audio_muted'):
                self.audio_muted = not self.audio_muted
            else:
                self.audio_muted = True
            
            if self.audio_muted:
                self.mute_audio_btn.configure(image=self.audio_image_ctk_off)
                print("Audio muted")
            else:
                self.mute_audio_btn.configure(image=self.audio_image_ctk_on)
                print("Audio unmuted")
        
        return toggle_audio
    
    def add_left_panel_content(self):
        self._add_left_title()
        self._add_search_controls()
        self._add_progress_bar()
        self._add_description_frame()
        self._add_action_buttons()
    
    def add_right_panel_content(self):
        right_title = ctk.CTkLabel(
            self.master.right_panel,
            text="Console", 
            text_color="white",
            font=(self.master.preferred_font, 20, "bold"),
            fg_color="transparent"
        )
        right_title.place(relx=0.05, rely=0.02)

        self.master.right_console = ctk.CTkTextbox(
            self.master.right_panel,
            width=350,
            height=500,
            fg_color=("#FFFFFF", "#000000"),
            text_color='green',
            wrap='word',
            font=(self.master.preferred_font, self.master.preferred_size)
        )
        self.master.right_console.place(relx=0.05, rely=0.1)
    
    def _add_left_title(self):
        left_title = ctk.CTkLabel(
            self.master.left_panel,
            text="PC Parts Web Scraper",
            text_color="white",
            font=(self.master.preferred_font, self.master.preferred_size, "bold"),
            fg_color="transparent"
        )
        left_title.place(relx=0.05, rely=0.02)

    def _get_website_selection_callback(self):
        """Get the callback for website selection"""
        if hasattr(self.master, 'gui') and hasattr(self.master.gui, 'on_selection_instantiate'):
            return self.master.gui.on_selection_instantiate
        elif hasattr(self.master, 'on_selection_instantiate'):
            return self.master.on_selection_instantiate
        else:
            def default_callback(value):
                print(f"Website selected: {value}")
                if hasattr(self.master, 'selected_website'):
                    self.master.selected_website = value
            return default_callback

    def _get_part_selection_callback(self):
        """Get the callback for part selection"""
        if hasattr(self.master, 'on_selection'):
            return self.master.on_selection
        else:
            def default_callback(value):
                print(f"Part selected: {value}")
                if hasattr(self.master, 'selected_pc_part'):
                    self.master.selected_pc_part = value
            return default_callback
        
    def _add_search_controls(self):
        self.master.left_entry = ctk.CTkEntry(
            self.master.left_panel, 
            width=300, 
            height=40, 
            corner_radius=20, 
            text_color=("black", "white"),
            placeholder_text='Enter your desired part here ...',
            placeholder_text_color=("#666666", "#888888"),
            font=(self.master.preferred_font, self.master.preferred_size)
        )
        self.master.left_entry.place(relx=0.05, rely=0.1)

        self.master.left_part_select = ctk.CTkComboBox(
            self.master.left_panel,
            width=170,  
            height=40,
            fg_color=("#FFFFFF", "#1A1A1A"),
            values=self.part_options,
            corner_radius=20,  
            text_color=("black", "white"),  
            dropdown_fg_color=("#FFFFFF", "#1A1A1A"),  
            dropdown_text_color=("black", "white"),
            state='readonly',
            command=self.master.on_selection,
            font=(self.master.preferred_font, 15)
        )
        self.master.left_part_select.set("GPU")
        self.master.left_part_select.place(relx=0.6, rely=0.02)

        # here we create the multi-choice component based on the website values we can choose from

        self.master.left_website_select = ctk.CTkComboBox(
            self.master.left_panel,
            width=170,  
            height=40,
            fg_color=("#FFFFFF", "#1A1A1A"),
            values=self.website_options,
            corner_radius=20,
            border_color=[self.master.primary_color, self.master.secondary_color],
            text_color=("black", "white"),  
            dropdown_text_color=("black", "white"),
            state='readonly',
            command=self._get_website_selection_callback,
            font=(self.master.preferred_font, 15)
        )
        self.master.left_website_select.set('Desktop.bg')
        self.master.left_website_select.place(relx=0.6, rely=0.1)
    
    def _add_progress_bar(self):
        self.master.progress_bar = ctk.CTkProgressBar(
            self.master.left_panel,
            width=1000,
            height=40,
            corner_radius=20,
        )
        self.master.progress_bar.place(relx=0.05, rely=0.2, relwidth=0.9)

        self.master.status_label = ctk.CTkLabel(
            self.master.left_panel,
            text="Ready to scrape...",
            text_color=("black", "white"),
            font=(self.master.preferred_font, self.master.preferred_size),
            fg_color="transparent"
        )
        self.master.status_label.place(relx=0.05, rely=0.25)
    
    def _add_description_frame(self):
        left_frame_label_container = ctk.CTkFrame(
            self.master.left_panel, 
            width=600, 
            height=400,
            fg_color=("#DBD8D8", "#232323"),
            border_width=2,
            border_color=("#FFFFFF", "#1A1A1A"),
            corner_radius=30
        )
        left_frame_label_container.place(relx=0.09, rely=0.4)

        left_label_container = ctk.CTkFrame(
            left_frame_label_container,
            fg_color="transparent"
        )
        left_label_container.pack(fill='both', expand=True, padx=100, pady=100)

        left_label_description = ctk.CTkLabel(
            left_label_container,
            text='Lorem Ipsum is simply dummy text of the printing and typesetting industry...',
            anchor='w',
            font=(self.master.preferred_font, self.master.preferred_size),
            justify='left',
            wraplength=450,  
        )
        left_label_description.pack(fill='both', expand=True, padx=10, pady=10)