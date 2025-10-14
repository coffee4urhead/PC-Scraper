import xlsxwriter
from datetime import datetime
import os

class TableMaker:
    def __init__(self, data, website_scraped, output_folder, pc_part_selected, currency_symbol=""):
        self.data = data
        self.website_scraped = website_scraped
        self.currency_symbol = currency_symbol or "$"
        self.pc_part_selected = pc_part_selected
        os.makedirs(output_folder, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = os.path.join(output_folder, f"{self.pc_part_selected}_Data_{timestamp}.xlsx")
        self.create_table()

    def create_table(self):
        workbook = xlsxwriter.Workbook(self.filename)
        worksheet = workbook.add_worksheet(f"{self.pc_part_selected} List of scraped data")

        header_format = workbook.add_format({
            'bold': True, 'font_color': 'white', 'bg_color': '#1F497D',
            'align': 'center', 'border': 1
        })
        
        currency_format = workbook.add_format({
            'num_format': f'"{self.currency_symbol}"#,##0.00',
            'align': 'right'
        })

        all_fields = set()
        for product in self.data:
            all_fields.update(product.keys())

        fixed_columns = ["title", "price", "url"]
        dynamic_columns = [field for field in sorted(all_fields)
                           if field not in fixed_columns]
        headers = ["Product Name", "Price", "URL"] + dynamic_columns
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        for row, product in enumerate(self.data, start=1):
            worksheet.write(row, 0, product.get("title", "N/A"))

            price_value = product.get("price", "N/A")
            
            if isinstance(price_value, (int, float)):
                worksheet.write(row, 1, price_value, currency_format)
            elif price_value == "N/A":
                worksheet.write(row, 1, "N/A")
            else:
                price_str = str(price_value).split("/")[0].strip()
                for symbol in ["лв", "$", "€", "£", "¥", "₩", "R$", "₹"]:
                    price_str = price_str.replace(symbol, "")
                try:
                    price_num = float(price_str)
                    worksheet.write(row, 1, price_num, currency_format)
                except ValueError:
                    worksheet.write(row, 1, str(price_value))
            
            worksheet.write(row, 2, product.get("url", "N/A"))

            for col, field in enumerate(dynamic_columns, start=3):
                worksheet.write(row, col, product.get(field, "N/A"))

        for col, header in enumerate(headers):
            max_len = len(header)
            for row in range(len(self.data)):
                value = str(product.get(header.lower().replace(" ", "_"), "N/A"))
                if len(value) > max_len:
                    max_len = len(value)
            worksheet.set_column(col, col, min(max_len + 2, 50))

        self._create_color_formatting(workbook, worksheet, self.data, self.pc_part_selected)

        if len(self.data) > 0:
            chart = workbook.add_chart({'type': 'column'})
            chart.add_series({
                'name': 'Price Distribution',
                'categories': f"='{self.pc_part_selected} List of scraped data'!$A$2:$A${len(self.data) + 1}",
                'values': f"='{self.pc_part_selected} List of scraped data'!$B$2:$B${len(self.data) + 1}",
                'fill': {'color': '#4C78DB'},
            })
            chart.set_title({'name': f'{self.pc_part_selected} Prices'})
            worksheet.insert_chart('J5', chart)

        workbook.close()
        print(f"File saved: {self.filename}")

    def _create_color_formatting(self, workbook, worksheet, data, part_selected):
        format_tier1 = workbook.add_format({'bg_color': '#D9F501'})  
        format_tier2 = workbook.add_format({'bg_color': '#F5EF00'})  
        format_tier3 = workbook.add_format({'bg_color': '#F58600'})  
        format_tier4 = workbook.add_format({'bg_color': '#F2320C'}) 

        price_ranges = {
            "Motherboard": [100, 200, 400],
            "PSU": [60, 120, 200],
            "Extension Cables": [60, 120, 200],
            "RAM": [50, 100, 200],
            "CPU": [100, 250, 500],
            "GPU": [200, 400, 800],
            "Case": [50, 100, 200],
            "Fans": [10, 20, 40],
            "AIO": [30, 80, 150],
            "Air Coolers": [30, 80, 150],
            "default": [50, 100, 200]
        }

        ranges = price_ranges.get(part_selected, price_ranges["default"])
        t1, t2, t3 = ranges

        worksheet.conditional_format(1, 0, len(data), len(data), {
            'type': 'formula',
            'criteria': f'=AND($B2>0, $B2<={t1})',
            'format': format_tier1
        })

        worksheet.conditional_format(1, 0, len(data), len(data), {
            'type': 'formula',
            'criteria': f'=AND($B2>{t1}, $B2<={t2})',
            'format': format_tier2
        })

        worksheet.conditional_format(1, 0, len(data), len(data), {
            'type': 'formula',
            'criteria': f'=AND($B2>{t2}, $B2<={t3})',
            'format': format_tier3
        })

        worksheet.conditional_format(1, 0, len(data), len(data), {
            'type': 'formula',
            'criteria': f'=$B2>{t3}',
            'format': format_tier4
        })