# 💼 PC Parts Scraper 🚀

**Your Smart Assistant for Building Dream PCs!** 

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)](https://python.org)
[![Web Scraping](https://img.shields.io/badge/Web-Scraping-orange?logo=web)](https://)
[![PC Building](https://img.shields.io/badge/PC-Building-green?logo=pcgaming)](https://)

## 🎯 What Problem Are We Solving?

> ⏳ **Tired of spending hours jumping between websites** to compare PC parts prices?
> 
> 💸 **Frustrated with missing out on the best deals** for your dream gaming rig?
> 
> 🔄 **Exhausted from manually tracking** prices across multiple retailers?

**PC Parts Scraper is your ultimate solution!** We automatically hunt down the best PC component deals across the web, so you can focus on what matters - building an awesome PC! 🖥️✨

---

## ✨ Magic Features

### 🔍 **Smart Part Detection**
- **Multi-website scanning** - We search across popular PC part retailers simultaneously
- **Real-time price tracking** - Get the latest prices without refreshing multiple tabs
- **Intelligent categorization** - CPUs, GPUs, RAM, Motherboards, and more!

### 📊 **Comparison Superpowers**
```python
# We turn this chaos:
# - Website A: RTX 4080 - $1199
# - Website B: RTX 4080 - $1149
# - Website C: RTX 4080 - $1249

# Into this clarity:
# 🏆 BEST DEAL: RTX 4080 - $1149 (Website B)
```

### 🗂️ Main Page

- Displays a search GUI where people can interact with the field typing in the product that they are looking for 

- This is also the place where you select the website you want to be scraped and just ***sit*** and ***watch*** as the ***progress bar*** fills up to 100%

- You also have the ***Select Save Folder*** functionality where you can select where do you want the excel spreadsheet to be saved on you system.

- The excel spreadsheet which is the final result of the scraping is made from three ***required*** fields: Product Name, Price and URl. There are also technical specifications which are filled with nothing if there is no technical spec that has been scraped for a previous product offering.

## 🌟 User Options Menu

- This menu contains setting regarding the font, currency setttings, price formatting, browser options and choosing the application theme

***Fonts***: Arial, Courier New, Georgia, Times New Roman and Verdana

***Currency Settings***: you can choose the currency you want the scraped prices to be converted to. You can choose from USD, EUR, GBP, JPY, BGN, BRL, CAD. We can always expand our currency options by adding more.

***Price Formatting***: You can have your price formatted in a custom preferred type or have it done to an integer value instead!

***Browser Options***: Choose from various website browsers like MS Edge, Brave, Firefox, Safari or Chromium. Keep in mind Chromium is the ***default*** browser even if you select a browser which you don't have installed on your system currently.

***Application Theme***: Choose whether your like dark themed or full white.

### 🔍 File and Help menu

- ***Close the file*** from the ***Help*** menu
- ***Help** menu shows information about the project and the creator in general

---
### Follow these steps to get the PC-Parts-Scraper application up and running on your local machine for development and testing purposes.
---

### **Client Application Setup**

1. **Clone the Repository**:  
   You can clone the repository using the following command or download it as a ZIP file and extract it on your
   computer.

   ```bash
   git clone https://github.com/coffee4urhead/PC-Scraper.git
   ```

2. **Navigate to the Project Directory**:  
   Use the terminal to navigate to the project directory.

   ```bash
   cd PC-Scraper
   ```

4. **Install Dependencies**:  
   Install all the necessary dependencies by running the following command in your terminal:

   ```bash
   pip install -r requirements.txt
   ```
5. **Create your own API keys**:  
   I am currently using this currency conversion API in my application: ***https://unirateapi.com/*** which i would like to give special thanks to provided that the API is completely free and with unlimited usage!

---

🛠️ **Technologies and Tools**

<p align="left">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/python/python-original.svg" width="40" height="40" />
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/playwright/playwright-original.svg" width="40" height="40" />
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/selenium/selenium-original.svg" width="40" height="40" />
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/socketio/socketio-original.svg" width="40" height="40" />
</p>

---

### 📚 Libraries

### 🛠️ Tech Stack & Libraries

**Powered by these awesome tools:** 

| Category | Libraries & Tools |
|----------|-------------------|
| **🕸️ Web Scraping** | `playwright==1.55.0`, `selenium==4.36.0`, `beautifulsoup4==4.14.2`, `requests==2.32.5` |
| **📊 Data Processing** | `pandas==2.3.1`, `xlsxwriter==3.2.9`, `sortedcontainers==2.4.0` |
| **🎨 Image & GUI** | `pillow==11.3.0`, `pygame==2.6.1` |
| **⚡ Async Operations** | `trio==0.31.0`, `trio-websocket==0.12.2`, `websockets==15.0.1` |
| **🔧 Development** | `black==25.9.0`, `python-dotenv==1.1.1`, `mypy_extensions==1.1.1` |
| **🌐 Web Automation** | `webdriver-manager==4.0.2`, `websocket-client==1.9.0` |
| **🔒 Security & Networking** | `certifi==2025.10.5`, `urllib3==2.5.0`, `PySocks==1.7.1` |

---

### 🔧 Core Dependencies Deep Dive

#### **Web Scraping Powerhouse 🕷️**
```python
# Your scraping toolkit includes:
- playwright==1.55.0      # Modern browser automation
- selenium==4.36.0        # Web driver control  
- beautifulsoup4==4.14.2  # HTML parsing magic
- requests==2.32.5        # HTTP requests made easy
```

🛠️ **Key Integrations**:

- **Tkinter** for GUI and visualization
- **XLSwriter** via psycopg2 for database operations