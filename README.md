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
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/redis/redis-original.svg" width="40" height="40" />
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/plotly/plotly-original-wordmark.svg" width="40" height="40"/>
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/postgresql/postgresql-original-wordmark.svg" width="40" height="40" />
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/sass/sass-original.svg" width="40" height="40" />
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/socketio/socketio-original-wordmark.svg" width="40" height="40"/>
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/pandas/pandas-original-wordmark.svg" width="40" height="40"/>
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/ngrok/ngrok-original.svg" width="40" height="40"/>
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/django/django-plain.svg" width="40" height="40"/>
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/djangorest/djangorest-line.svg" width="40" height="40"/>
</p>

---

### 📚 Libraries

- **pdf2image==1.17.0** – Converts PDF documents to images (supports PNG/JPEG formats)
- **pandas==2.3.1** – Data analysis and manipulation tool for structured data operations
- **numpy==2.3.2** – Fundamental package for numerical computing with array support
- **ngrok==1.4.0** – Secure tunneling service for exposing local servers to the internet
- **pillow==11.2.1** – Python Imaging Library for image processing capabilities
- **djangorestframework==3.16.0** – Toolkit for building Web APIs with Django
- **channels==4.2.2** – Extends Django to handle WebSockets and async protocols
- **channels_redis==4.2.1** – Redis channel layer backend for Django Channels
- **django-stripe-payments==2.0.0** – Django integration for Stripe payment processing
- **django-compressor==4.1** – Combines and minifies static files (CSS/JS)
- **cryptography==45.0.5** – Provides cryptographic recipes and primitives
- **daphne==4.2.1** – HTTP/WebSocket protocol server for Django Channels
- **Django==5.0.1** – High-level Python web framework (core dependency)
- **plotly==6.2.0** – Interactive graphing library for data visualization
- **psycopg2==2.9.10** – PostgreSQL database adapter for Python
- **python-dotenv==1.1.1** – Reads key-value pairs from .env files
- **stripe==12.3.0** – Official Stripe API library for payment processing

🛠️ **Key Integrations**:

- **Stripe** for payment processing
- **PostgreSQL** via psycopg2 for database operations
- **Redis** for Channels backend
- **Plotly** for admin dashboard visualizations