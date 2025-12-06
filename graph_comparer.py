import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import customtkinter as ctk
from pathlib import Path
from datetime import datetime
import os
import re

class GraphComparer:
    def __init__(self, comparison_data, file_format, parent_window=None):
        """
        Initialize GraphComparer with comparison data
        
        Args:
            comparison_data: Dictionary from HistoricalComparison.get_summary()['data']
            file_format: 'CSV' or 'JSON'
            parent_window: Parent CTk window for embedding plots
        """
        self.comparison_data = comparison_data
        self.file_format = file_format.lower()
        self.parent_window = parent_window
        self.figures = []
        
        self.first_website_data = self._load_website_data('first_website')
        self.second_website_data = self._load_website_data('second_website')

        if parent_window:
            self.create_embedded_plots(parent_window)
        else:
            self.create_standalone_window()
    
    def _load_website_data(self, website_key):
        """Load data for a specific website"""
        try:
            website_info = self.comparison_data[website_key]
            base_path = Path("./scrape-history/data") / self.file_format
            website_path = base_path / website_info['name'] / self.comparison_data['part']
        
            all_data = []
        
            for filename in website_info['files'][:10]:  
                file_path = website_path / filename
                data = self._read_file(file_path)
                if data is not None:
                    date_str = self._extract_date_from_filename(filename)
                    for item in data:
                        if isinstance(item, dict):
                            item['date'] = date_str  
                            item['website'] = website_info['name']
                    all_data.extend(data)
        
            return all_data
        
        except Exception as e:
            print(f"Error loading {website_key} data: {e}")
            return []
    
    def _read_file(self, file_path):
        """Read file based on format"""
        try:
            if self.file_format == 'json':
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif self.file_format == 'csv':
                return pd.read_csv(file_path).to_dict('records')
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
    
    def _extract_date_from_filename(self, filename):
        """Extract date from filename"""
        try:
            date_pattern = r'(\d{4}-\d{2}-\d{2})'
            match = re.search(date_pattern, filename)
            if match:
                return match.group()  
            return "Unknown"
        except:
            return "Unknown"
    
    def _prepare_price_data(self):
        """Prepare price data for visualization"""
        df1 = pd.DataFrame(self.first_website_data)
        df2 = pd.DataFrame(self.second_website_data)
    
        print(f"\nDEBUG _prepare_price_data:")
        print(f"df1 columns: {df1.columns.tolist()}")
        print(f"df2 columns: {df2.columns.tolist()}")
        print(f"df1 shape: {df1.shape}")
        print(f"df2 shape: {df2.shape}")
    
        if df1.empty or df2.empty:
            print("One or both DataFrames are empty!")
            return None, None, []
    
        for df in [df1, df2]:
            if 'price' in df.columns:
                print(f"Cleaning price column. Sample before: {df['price'].head().tolist()}")
                df['price_numeric'] = self._clean_price_column(df['price'])
                print(f"Sample after: {df['price_numeric'].head().tolist()}")
                print(f"Non-null prices: {df['price_numeric'].notna().sum()}/{len(df)}")
        
            if 'date' in df.columns:
                print(f"Date column found. Sample: {df['date'].head().tolist()}")
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                print(f"Valid dates after conversion: {df['date'].notna().sum()}/{len(df)}")
            else:
                print("WARNING: No date column found in DataFrame!")

        has_dates1 = 'date' in df1.columns and df1['date'].notna().any()
        has_dates2 = 'date' in df2.columns and df2['date'].notna().any()
    
        print(f"\nDate status:")
        print(f"Website 1 has dates: {has_dates1}")
        print(f"Website 2 has dates: {has_dates2}")
    
        return df1, df2, []
    
    def _clean_price_column(self, price_series):
        """
        Clean price column with various formats
        Handles: 'Ft24929.13', '24929.13 Ft', '24,929.13', etc.
        """
        if price_series.empty:
            return pd.Series([], dtype=float)
    
        prices = price_series.astype(str)
    
        prices = prices.str.replace(r'[^\d.,]', '', regex=True)
    
        if prices.str.contains(r'\d+,\d{2}$').any():
            prices = prices.str.replace('.', '', regex=False)  
            prices = prices.str.replace(',', '.', regex=False)  
        else:
            prices = prices.str.replace(',', '', regex=False)  
    
        return pd.to_numeric(prices, errors='coerce')   
    
    def create_basic_comparison_plot(self, parent_frame):
        """Create basic comparison plot that works without dates"""
        df1, df2, _ = self._prepare_price_data()
    
        if df1 is None or df2 is None or df1.empty or df2.empty:
            self._show_no_data_message(parent_frame, "No data available for comparison")
            return

        fig = Figure(figsize=(12, 8), dpi=100)
    
        ax1 = fig.add_subplot(221)
    
        price_data = []
        labels = []
    
        for df, name in [(df1, self.comparison_data['first_website']['name']),
                        (df2, self.comparison_data['second_website']['name'])]:
            if 'price_numeric' in df.columns:
                prices = df['price_numeric'].dropna().values
                if len(prices) > 0:
                    price_data.append(prices)
                    labels.append(name)
    
        if price_data:
            box = ax1.boxplot(price_data, labels=labels, patch_artist=True)
            colors = ['lightblue', 'lightcoral']
            for patch, color in zip(box['boxes'], colors):
                patch.set_facecolor(color)
        
            ax1.set_title('Price Distribution Comparison', fontsize=12, fontweight='bold')
            ax1.set_ylabel('Price (Ft)')
            ax1.grid(True, alpha=0.3, axis='y')

            stats_text = ""
            for i, (prices, label) in enumerate(zip(price_data, labels)):
                stats_text += f"{label}:\n"
                stats_text += f"  Min: {np.min(prices):.0f} Ft\n"
                stats_text += f"  Avg: {np.mean(prices):.0f} Ft\n"
                stats_text += f"  Max: {np.max(prices):.0f} Ft\n"
                stats_text += f"  Count: {len(prices)}\n\n"
        
            ax1.text(1.02, 0.98, stats_text.strip(),
                transform=ax1.transAxes, fontsize=8,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        else:
            ax1.text(0.5, 0.5, 'No price data available',
                horizontalalignment='center', verticalalignment='center',
                transform=ax1.transAxes)
            ax1.axis('off')
    
        ax2 = fig.add_subplot(222)
    
        counts = [len(df1), len(df2)]
        website_names = [self.comparison_data['first_website']['name'],
                    self.comparison_data['second_website']['name']]
    
        bars = ax2.bar(website_names, counts, color=['blue', 'red'], alpha=0.7)
        ax2.set_title('Total Products Comparison', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Number of Products')
    
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{count}', ha='center', va='bottom', fontweight='bold')
    
        ax2.grid(True, alpha=0.3, axis='y')
    
        ax3 = fig.add_subplot(223)
    
        if 'price_numeric' in df1.columns and 'price_numeric' in df2.columns:
            price_stats = []
            for df, name, color in [(df1, website_names[0], 'blue'),
                                (df2, website_names[1], 'red')]:
                prices = df['price_numeric'].dropna()
                if len(prices) > 0:
                    price_stats.append({
                        'name': name,
                        'min': prices.min(),
                        'mean': prices.mean(),
                        'max': prices.max(),
                        'color': color
                    })
        
            if price_stats:
                y_pos = np.arange(len(price_stats))
                width = 0.6
            
                for i, stats in enumerate(price_stats):
                    ax3.plot([i, i], [stats['min'], stats['max']], 
                        color=stats['color'], linewidth=3, alpha=0.5)
                    ax3.plot(i, stats['mean'], 'o', color=stats['color'], 
                            markersize=10, label=f"{stats['name']} (Avg)")
            
                ax3.set_xticks(y_pos)
                ax3.set_xticklabels([s['name'] for s in price_stats])
                ax3.set_title('Price Range Comparison', fontsize=12, fontweight='bold')
                ax3.set_ylabel('Price (Ft)')
                ax3.legend()
                ax3.grid(True, alpha=0.3)
            else:
                ax3.text(0.5, 0.5, 'No price data for range plot',
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax3.transAxes)
                ax3.axis('off')
        else:
            ax3.text(0.5, 0.5, 'Price data not available',
                horizontalalignment='center', verticalalignment='center',
                transform=ax3.transAxes)
            ax3.axis('off')
    
        ax4 = fig.add_subplot(224)
    
        all_products = []
        for df, website in [(df1, website_names[0]), (df2, website_names[1])]:
            if 'price_numeric' in df.columns and 'title' in df.columns:
                products = df[['title', 'price_numeric']].copy()
                products['website'] = website
                all_products.append(products)
    
        if all_products:
            combined = pd.concat(all_products, ignore_index=True)
            top_10 = combined.nlargest(10, 'price_numeric')
        
            top_10['short_title'] = top_10['title'].apply(
            lambda x: (x[:40] + '...') if len(x) > 40 else x
            )
        
            y_pos = np.arange(len(top_10))
            colors = ['blue' if w == website_names[0] else 'red' for w in top_10['website']]
        
            bars = ax4.barh(y_pos, top_10['price_numeric'], color=colors, alpha=0.7)
            ax4.set_yticks(y_pos)
            ax4.set_yticklabels(top_10['short_title'], fontsize=8)
            ax4.set_xlabel('Price (Ft)')
            ax4.set_title('Top 10 Most Expensive Products', fontsize=12, fontweight='bold')
            ax4.invert_yaxis()  
        
            for bar, price in zip(bars, top_10['price_numeric']):
                width = bar.get_width()
                ax4.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                    f'{price:.0f} Ft', ha='left', va='center', fontsize=8)
        else:
            ax4.text(0.5, 0.5, 'No product data for top products',
                horizontalalignment='center', verticalalignment='center',
                transform=ax4.transAxes)
            ax4.axis('off')
    
        fig.suptitle(f"{self.comparison_data['part']} Comparison: {website_names[0]} vs {website_names[1]}",
                fontsize=14, fontweight='bold', y=0.98)
    
        fig.tight_layout(rect=[0, 0, 1, 0.96]) 
    
        canvas = FigureCanvasTkAgg(fig, parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        self.figures.append(canvas)
    
    def create_price_distribution_plot(self, parent_frame):
        """Create price distribution comparison plot"""
        df1, df2, _ = self._prepare_price_data()
        
        if df1 is None or df2 is None:
            return
        
        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        def remove_outliers(df, column):
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            return df[(df[column] >= Q1 - 1.5*IQR) & (df[column] <= Q3 + 1.5*IQR)]
        
        df1_clean = remove_outliers(df1, 'price_numeric')
        df2_clean = remove_outliers(df2, 'price_numeric')
        
        bins = np.linspace(0, max(df1_clean['price_numeric'].max(), 
                                df2_clean['price_numeric'].max()), 30)
        
        ax.hist(df1_clean['price_numeric'], bins=bins, alpha=0.5, 
               label=self.comparison_data['first_website']['name'], color='blue')
        ax.hist(df2_clean['price_numeric'], bins=bins, alpha=0.5, 
               label=self.comparison_data['second_website']['name'], color='red')
        
        ax.set_title('Price Distribution Comparison', fontsize=14, fontweight='bold')
        ax.set_xlabel('Price')
        ax.set_ylabel('Frequency')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        self.figures.append(canvas)
    
    def create_product_count_plot(self, parent_frame):
        """Create product count comparison plot"""
        df1, df2, _ = self._prepare_price_data()
        
        if df1 is None or df2 is None:
            return
        
        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        count1 = df1.groupby('date').size().reset_index(name='count')
        count2 = df2.groupby('date').size().reset_index(name='count')
        
        dates = sorted(set(count1['date']).union(set(count2['date'])))
        dates_str = [d.strftime('%Y-%m-%d') for d in dates]
        
        count1_dict = dict(zip(count1['date'], count1['count']))
        count2_dict = dict(zip(count2['date'], count2['count']))
        
        counts1 = [count1_dict.get(d, 0) for d in dates]
        counts2 = [count2_dict.get(d, 0) for d in dates]
        
        x = np.arange(len(dates))
        width = 0.35
        
        ax.bar(x - width/2, counts1, width, 
              label=self.comparison_data['first_website']['name'], color='blue')
        ax.bar(x + width/2, counts2, width, 
              label=self.comparison_data['second_website']['name'], color='red')
        
        ax.set_title('Product Count Comparison Over Time', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Number of Products')
        ax.set_xticks(x)
        ax.set_xticklabels(dates_str, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        self.figures.append(canvas)
    
    def create_embedded_plots(self, parent_frame):
        """Create embedded plots in the given parent frame"""
        for widget in parent_frame.winfo_children():
            widget.destroy()
    
        tabview = ctk.CTkTabview(parent_frame)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)
    
        tab_basic = tabview.add("Basic Comparison")
        tab_price_dist = tabview.add("Price Analysis")
    
        for tab in [tab_basic, tab_price_dist]:
            tab.grid_columnconfigure(0, weight=1)
            tab.grid_rowconfigure(0, weight=1)
    
        self.create_basic_comparison_plot(tab_basic)
        self.create_price_distribution_plot(tab_price_dist) 
    
    def create_standalone_window(self):
        """Create a standalone window for visualization"""
        window = ctk.CTkToplevel()
        window.title(f"Price Comparison: {self.comparison_data['first_website']['name']} vs {self.comparison_data['second_website']['name']}")
        window.geometry("1200x800")
        
        self.create_embedded_plots(window)
        
        button_frame = ctk.CTkFrame(window)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(button_frame, text="Export All Plots", 
                     command=self.export_all_plots).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Close", 
                     command=window.destroy).pack(side="right", padx=5)
    
    def export_all_plots(self):
        """Export all figures to files"""
        for i, canvas in enumerate(self.figures):
            filename = f"plot_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            canvas.figure.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"Exported: {filename}")