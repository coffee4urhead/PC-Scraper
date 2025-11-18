import csv
import datetime 
import os

class CSVCreator:
    def __init__(self, data, website_scraped, output_folder, pc_part_selected, currency_symbol="", history_save_preferred=True):
        self.data = data
        self.website_scraped = website_scraped
        self.currency_symbol = currency_symbol or "$"
        self.pc_part_selected = pc_part_selected
        self.history_save_preferred = history_save_preferred

        os.makedirs(output_folder, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") 
        self.filename = os.path.join(output_folder, f"{self.pc_part_selected}_Data_{timestamp}.csv")

        self.create_csv()
        
        if self.history_save_preferred:
            self.create_history_copy(timestamp)

    def create_csv(self):
        """Create the main CSV file"""
        if not self.data:
            print("⚠️ No data to save to CSV")
            return
            
        with open(self.filename, "w", newline='', encoding='utf-8') as csv_file:
            fieldnames = self._get_fieldnames()
            
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            
            for product in self.data:
                row = {field: product.get(field, '') for field in fieldnames}
                writer.writerow(row)
                
        print(f"CSV file created: {self.filename}")
        print(f"📊 Saved {len(self.data)} products to CSV")

    def _get_fieldnames(self):
        """Extract all possible fieldnames from the data"""
        fieldnames = set()
        for product in self.data:
            fieldnames.update(product.keys())
        return sorted(list(fieldnames))

    def create_history_copy(self, timestamp):
        """Create a copy in the scrape-history folder"""
        scrape_history_path = f"./scrape-history/data/csv/{self.website_scraped}/{self.pc_part_selected}/"
        os.makedirs(scrape_history_path, exist_ok=True)
        
        history_filename = os.path.join(scrape_history_path, f"{self.pc_part_selected}_{timestamp}.csv")
        
        if not self.data:
            print("⚠️ No data to save to history CSV")
            return
            
        with open(history_filename, "w", newline='', encoding='utf-8') as csv_file:
            fieldnames = self._get_fieldnames()
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            
            for product in self.data:
                row = {field: product.get(field, '') for field in fieldnames}
                writer.writerow(row)
                
        print(f"History copy created: {history_filename}")