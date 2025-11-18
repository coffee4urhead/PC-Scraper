import json
import datetime 
import os

class JSONCreator:
    def __init__(self, data, website_scraped, output_folder, pc_part_selected, currency_symbol="", history_save_preferred=True):
        self.data = data
        self.website_scraped = website_scraped
        self.currency_symbol = currency_symbol or "$"
        self.pc_part_selected = pc_part_selected
        self.history_save_preferred = history_save_preferred

        os.makedirs(output_folder, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") 
        self.filename = os.path.join(output_folder, f"{self.pc_part_selected}_Data_{timestamp}.json")

        self.create_json()
        
        if self.history_save_preferred:
            self.create_history_copy(timestamp)

    def create_json(self):
        """Create the main JSON file"""
        with open(self.filename, "w") as json_file:
            json.dump(self.data, json_file, ensure_ascii=False, indent=4)
        print(f"JSON file created: {self.filename}")

    def create_history_copy(self, timestamp):
        """Create a copy in the scrape-history folder"""
        scrape_history_path = f"./scrape-history/data/json/{self.website_scraped}/{self.pc_part_selected}/"
        os.makedirs(scrape_history_path, exist_ok=True)
        
        history_filename = os.path.join(scrape_history_path, f"{self.pc_part_selected}_{timestamp}.json")
        
        with open(history_filename, "w") as json_file:
            json.dump(self.data, json_file, ensure_ascii=False, indent=4)
        print(f"History copy created: {history_filename}")