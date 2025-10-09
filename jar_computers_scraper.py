import re
from urllib.parse import quote, urljoin

from base_scraper import BaseScraper

class JarComputersScraper(BaseScraper):
    def __init__(self, update_gui_callback=None, driver=None):
        super().__init__(update_gui_callback, driver)
        self.base_url = "https://www.jarcomputers.com/"
        self.exclude_keywords = [
            "Лаптоп", 'Настолен компютър', 'HP Victus', 'Acer Predator Helios'
        ]

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)
        #https://www.jarcomputers.com/search?q=nxzt+case
        return (
            f"{self.base_url}search?q={encoded_term}"
        )

    def _construct_page_url(self, base_url, search_term, page):
        if page > 1:
            return f"{self.base_url}search?q={quote(search_term)}&ref=&page={page}"
        return base_url

    def _extract_product_links(self, soup):
        """Get all product links from a specific search results page URL"""
        product_links = []

        # Find the product list container
        product_list = soup.find('ol', {'id': 'product_list'})
        if not product_list:
            print("No product links found")
            return product_links

        # Find all product items - using CSS selector to match li elements that have class starting with 'sProduct'
        products = product_list.find_all('li', class_=lambda x: x and 'sProduct' in x.split())

        for product in products:
            if self.stop_event.is_set():
                break

            # Skip sponsored ads
            if product.find('span', string=re.compile('Sponsored')):
                continue

            # Find the link - adjust the selector based on actual HTML
            link_tag = product.find('a', href=True)
            title = product.find('span', {"class": "short_title fn"}).get_text(strip=True)
            is_unavailable = bool(product.find('span', {"class": "avail-old"}))

            if any(True for word in self.exclude_keywords if word.lower() in title.lower()):
                continue

            if is_unavailable:
                continue

            if link_tag and 'href' in link_tag.attrs:
                full_url = urljoin(self.base_url, link_tag['href'])
                clean_url = full_url.split('ref=')[0].split('?')[0]
                if clean_url not in product_links:
                    product_links.append(clean_url)

        return product_links

    def _parse_product_page(self, soup, product_url):
        """Extract detailed information from a product page and structure it for Excel output"""
        try:
            # Parse title
            title_tag = soup.find('div', {'id': 'product_name'})
            title = title_tag.find("h1").get_text(strip=True) if title_tag else "N/A"

            # Parse price
            price_tag = soup.find('div', {'class': 'price'})
            price = price_tag.get_text(strip=True).replace("лв", "") if price_tag else "N/A"

            product_data = {
                'title': title,
                'price': price,
                'url': product_url
            }

            # Parse technical properties (fail-safe)
            tech_table = soup.find('ul', {'class': 'pprop'})
            if tech_table:
                for item in tech_table.find_all('li'):  # Changed variable name from 'list' to 'item'
                    try:
                        label = item.get_text(strip=True).lower()
                        value_tag = item.find("b")
                        if value_tag:  # Only proceed if <b> tag exists
                            value = value_tag.get_text(strip=True)
                            product_data[label] = value
                    except Exception as e:
                        print(f"Skipping invalid property: {str(e)}")
                        continue  # Skip this property but continue parsing others

            self._update_gui({"type": "product", 'data': product_data})
            return product_data

        except Exception as e:
            self._update_gui({'type': 'error', 'message': f"Product page error: {str(e)}"})
            return None