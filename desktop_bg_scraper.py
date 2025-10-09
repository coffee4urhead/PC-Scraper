import re
from urllib.parse import quote, urljoin

from base_scraper import BaseScraper


class DesktopScraper(BaseScraper):
    def __init__(self, update_gui_callback=None, driver=None):
        super().__init__(update_gui_callback, driver)
        self.base_url = "https://desktop.bg/"

        self.exclude_keywords = [
            "Лаптоп", 'Настолен компютър', 'HP Victus', 'Acer Predator Helios'
        ]


    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)
        #https://desktop.bg/search?q=nvidia+rtx+5060
        return (
            f"{self.base_url}search?q={encoded_term}"
        )

    def _construct_page_url(self, base_url, search_term, page):
        if page > 1:
            #https://desktop.bg/search?page=2&q=nvidia+rtx+4060
            return f"{self.base_url}search?page={page}&q={quote(search_term)}"
        return base_url

    def _extract_product_links(self, soup):
        """Get all product links from a specific search results page URL"""
        product_links = []

        product_list = soup.find('ul', {'class': 'products'})
        if not product_list:
            print("No product links found")
            return product_links
        
        products = product_list.find_all('li', id=re.compile('^product_[0-9]+$'))

        for product in products:
            if self.stop_event.is_set():
                break

            link_tag = product.find('a', href=True)

            if link_tag and 'href' in link_tag.attrs:
                full_url = urljoin(self.base_url, link_tag['href'])
                clean_url = full_url.split('ref=')[0].split('?')[0]
                if clean_url not in product_links:
                    product_links.append(clean_url)

        return product_links

    def _parse_product_page(self, soup, product_url):
        """Extract detailed information from a product page and structure it for Excel output"""
        try:
            title_tag = soup.find('div', {'id': 'content'})
            title = title_tag.find('h1', {"itemprop": "name"}).get_text(strip=True) if title_tag else "N/A"

            price_tag = soup.find('span', {'itemprop': 'price'})
            price = price_tag.get_text(strip=True).replace("лв", "") if price_tag else "N/A"

            product_data = {
                'title': title,
                'price': price,
                'url': product_url
            }

            tech_table = soup.find('table', {'class': 'product-characteristics'})
            if tech_table:
                for item in tech_table.find_all('tr'):
                    try:
                        label = item.find('th', {'scope': 'row'}).get_text(strip=True).lower()

                        if label == "описание":
                            continue
                        else:
                            value = item.find("td").get_text(strip=True).lower()
                            product_data[label] = value

                    except Exception as e:
                        print(f"Skipping invalid property: {str(e)}")
                        continue

            self._update_gui({"type": "product", 'data': product_data})
            return product_data

        except Exception as e:
            self._update_gui({'type': 'error', 'message': f"Product page error: {str(e)}"})
            return None