import xlsxwriter
from datetime import datetime
import os

class TableMaker:
    def __init__(self, data, website_scraped, output_folder):
        self.data = data
        self.website_scraped = website_scraped
        # Create folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)

        # Define filename with folder path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = os.path.join(output_folder, f"GPU_Data_{timestamp}.xlsx")

        self.create_table()

    def create_table(self):
        workbook = xlsxwriter.Workbook(self.filename)
        worksheet = workbook.add_worksheet("GPU List of scraped data")

        header_format = workbook.add_format({
            'bold': True,
            'font_color': 'white',
            'bg_color': '#1F497D',
            'align': 'center',
            'border': 1
        })
        currency_format = workbook.add_format({
            'num_format': '$#,##0.00',
            'align': 'right'
        })

        column_headers = ["Product Name", "GPU Brand", "GPU model", "Price", 'URL', 'Graphics Coprocessor', 'Graphics Ram Size', 'GPU Clock Speed', 'Video Output Resolution']
        for col, header in enumerate(column_headers):
            worksheet.write(0, col, header, header_format)

        # Write data rows
        for row, product in enumerate(self.data, start=1):
            worksheet.write(row, 0, product.get("title", "N/A"))
            worksheet.write(row, 1, product.get("brand", "N/A"))
            worksheet.write(row, 2, product.get("gpu_model", "N/A"))

            price_str = product.get("price", "$0").replace('$', '').replace(',', '.')
            try:
                price_num = float(price_str)
                worksheet.write(row, 3, price_num, currency_format)
            except ValueError:
                worksheet.write(row, 3, "N/A")

            worksheet.write(row, 4, product.get("url", "N/A"))
            worksheet.write(row, 5, product.get("graphics_coprocessor", "N/A"))
            #'Graphics Ram Size', 'GPU Clock Speed', 'Video Output Interface'
            worksheet.write(row, 6, product.get("graphics_ram_size", "N/A"))
            worksheet.write(row, 7, product.get("gpu_clock_speed", "N/A"))
            worksheet.write(row, 8, product.get("video_output_resolution", "N/A"))

        column_widths = [40, 15, 20, 20, 60, 25, 20, 15, 22]
        for col_idx, width in enumerate(column_widths):
            worksheet.set_column(col_idx, col_idx, width)

        chart = workbook.add_chart({'type': 'column'})
        chart.add_series({
            'name': 'Price Distribution',
            'categories': f"='GPU List of scraped data'!$A$2:$A${len(self.data) + 1}",
            'values': f"='GPU List of scraped data'!$D$2:$D${len(self.data) + 1}",
            'fill': {'color': '#4C78DB'},
        })
        chart.set_title({'name': 'GPU Prices'})
        worksheet.insert_chart('J5', chart)

        workbook.close()
        print(f"File saved: {self.filename}")


if __name__ == "__main__":
    sample_data = [
        {
            "title": "NVIDIA GeForce RTX 4090 Founders Edition",
            "price": "$1,599.99",
            "brand": "NVIDIA",
            "gpu_model": "RTX 4090",
            "url": "https://amazon.com/nvidia-rtx4090",
            "graphics_coprocessor": "NVIDIA GeForce RTX 4090",
            "graphics_ram_size": "24 GB GDDR6X",
            "gpu_clock_speed": "2.23 GHz",
            "video_output_resolution": "7680 x 4320"
        },
        {
            "title": "ASUS ROG Strix RTX 4080 OC Edition",
            "price": "$1,199.99",
            "brand": "ASUS",
            "gpu_model": "RTX 4080",
            "url": "https://amazon.com/asus-rtx4080",
            "graphics_coprocessor": "NVIDIA GeForce RTX 4080",
            "graphics_ram_size": "16 GB GDDR6X",
            "gpu_clock_speed": "2.21 GHz",
            "video_output_resolution": "7680 x 4320"
        },
        {
            "title": "MSI Gaming GeForce RTX 4070 Ti",
            "price": "$799.99",
            "brand": "MSI",
            "gpu_model": "RTX 4070 Ti",
            "url": "https://amazon.com/msi-rtx4070ti",
            "graphics_coprocessor": "NVIDIA GeForce RTX 4070 Ti",
            "graphics_ram_size": "12 GB GDDR6X",
            "gpu_clock_speed": "2.31 GHz",
            "video_output_resolution": "7680 x 4320"
        },
        {
            "title": "AMD Radeon RX 7900 XTX",
            "price": "$999.99",
            "brand": "AMD",
            "gpu_model": "RX 7900 XTX",
            "url": "https://amazon.com/amd-rx7900xtx",
            "graphics_coprocessor": "AMD Radeon RX 7900 XTX",
            "graphics_ram_size": "24 GB GDDR6",
            "gpu_clock_speed": "2.3 GHz",
            "video_output_resolution": "7680 x 4320"
        }
    ]

    TableMaker(
        data=sample_data,
        website_scraped="Amazon",
        output_folder="Amazon web search"
    )

    print("Test completed successfully. Check the 'Amazon web search' folder for the output file.")