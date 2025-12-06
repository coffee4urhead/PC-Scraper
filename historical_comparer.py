import os
import json
from datetime import datetime
from pathlib import Path

class HistoricalComparison:
    def __init__(self, file_format, part_for_comparison, first_website, second_website):
        self.file_format = file_format
        self.part_for_comparison = part_for_comparison
        self.first_website = first_website
        self.second_website = second_website
        self.first_website_files = []
        self.second_website_files = []
        self.error_message = ""
        self.success = False
        self.comparison_data = {}
        
        self.initialize_comparison()
    
    def initialize_comparison(self):
        """Initialize the comparison and check file availability"""
        if not all([self.file_format, self.part_for_comparison, self.first_website, self.second_website]):
            self.error_message = "Missing required parameters"
            return

        format_lower = self.file_format.lower().strip()
        if format_lower not in ['json', 'csv']:
            self.error_message = f"Unsupported file format: {self.file_format}"
            return

        if self._check_file_availability():
            self._load_comparison_data()
    
    def _check_file_availability(self):
        """Check if both websites have historical files"""
        try:
            base_path = Path("./scrape-history/data")
            
            first_path = base_path / self.file_format.lower() / self.first_website / self.part_for_comparison
            second_path = base_path / self.file_format.lower() / self.second_website / self.part_for_comparison

            if not first_path.exists() and not second_path.exists():
                self.error_message = f"Part information for {self.part_for_comparison} not found for {self.first_website} and {self.second_website}. Run a scrape on both wesbites for the particular part and then compare"
                return False

            if not first_path.exists():
                self.error_message = f"Part information for {self.part_for_comparison} not found for {self.first_website}. Run a scrape on {self.first_website} wesbite for the particular part and then compare"
                return False
            
            if not second_path.exists():
                self.error_message = f"Part information for {self.part_for_comparison} not found for {self.second_website}. Run a scrape on {self.second_website} wesbite for the particular part and then compare"
                return False
            
            self.first_website_files = [f.name for f in first_path.iterdir() if f.is_file() and not f.name.startswith('.')]
            self.second_website_files = [f.name for f in second_path.iterdir() if f.is_file() and not f.name.startswith('.')]

            self.first_website_files.sort(key=self._extract_date_from_filename, reverse=True)
            self.second_website_files.sort(key=self._extract_date_from_filename, reverse=True)
            
            if not self.first_website_files:
                self.error_message = f"No files found for {self.first_website}"
                return False
            
            if not self.second_website_files:
                self.error_message = f"No files found for {self.second_website}"
                return False
            
            return True
            
        except Exception as e:
            self.error_message = f"Error checking files: {str(e)}"
            return False
    
    def _extract_date_from_filename(self, filename):
        """Extract date from filename for sorting"""
        try:
            import re
            date_pattern = r'(\d{4})-(\d{2})-(\d{2})'
            match = re.search(date_pattern, filename)
            if match:
                return datetime.strptime(match.group(), "%Y-%m-%d")
            return datetime.min  
        except:
            return datetime.min
    
    def _load_comparison_data(self):
        """Load and prepare data for comparison"""
        try:
            self.comparison_data = {
                'first_website': {
                    'name': self.first_website,
                    'files': self.first_website_files,
                    'latest_file': self.first_website_files[0] if self.first_website_files else None,
                    'file_count': len(self.first_website_files)
                },
                'second_website': {
                    'name': self.second_website,
                    'files': self.second_website_files,
                    'latest_file': self.second_website_files[0] if self.second_website_files else None,
                    'file_count': len(self.second_website_files)
                },
                'part': self.part_for_comparison,
                'format': self.file_format,
                'comparison_ready': True
            }
            self.success = True
            
        except Exception as e:
            self.error_message = f"Error loading data: {str(e)}"
            self.success = False
    
    def get_summary(self):
        """Get a summary of the comparison setup"""
        if self.success:
            return {
                'status': 'ready',
                'message': f"Ready to compare {self.part_for_comparison} between {self.first_website} ({len(self.first_website_files)} files) and {self.second_website} ({len(self.second_website_files)} files)",
                'data': self.comparison_data
            }
        else:
            return {
                'status': 'error',
                'message': self.error_message,
                'data': None
            }
    
    def get_latest_files(self):
        """Get the latest files from both websites"""
        if not self.success:
            return None
        
        latest_files = {}
        base_path = Path("./scrape-history/data")
        
        try:
            if self.first_website_files:
                first_file_path = base_path / self.file_format.lower() / self.first_website / self.part_for_comparison / self.first_website_files[0]
                latest_files['first_website'] = self._read_file(first_file_path)
            
            if self.second_website_files:
                second_file_path = base_path / self.file_format.lower() / self.second_website / self.part_for_comparison / self.second_website_files[0]
                latest_files['second_website'] = self._read_file(second_file_path)
            
            return latest_files
            
        except Exception as e:
            self.error_message = f"Error reading files: {str(e)}"
            return None
    
    def _read_file(self, file_path):
        """Read file based on format"""
        if self.file_format.lower() == 'json':
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif self.file_format.lower() == 'csv':
            import csv
            with open(file_path, 'r', encoding='utf-8') as f:
                return list(csv.DictReader(f))
        return None