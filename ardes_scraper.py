import re
from urllib.parse import urljoin, quote
from base_scraper import BaseScraper


class ArdesScraper(BaseScraper):
    def __init__(self, update_gui_callback=None, driver=None):
        super().__init__(update_gui_callback, driver)
        self.base_domain = "https://www.ardes.bg"

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)

        return (
            f"https://www.ardes.bg/products?q={encoded_term}"
        )

    def _extract_product_links(self, soup):
        """Get all product links from a specific search results page URL"""
        product_links = []
        print(soup.prettify())
        print(soup.headers)
        products = soup.find_all('div', {'class': 'product-head'})

        for product in products:
            if self.stop_event.is_set():
                break

            # Skip sponsored ads

            link_tag = product.find('a', {'href': re.compile("^/products/")})
            if link_tag and 'href' in link_tag.attrs:
                full_url = urljoin(self.base_domain, link_tag['href'])
                clean_url = full_url.split('?')[0]
                if '/dp/' in clean_url and clean_url not in product_links:
                    product_links.append(clean_url)

        return product_links

    def _parse_product_page(self, soup, product_url):
        """Extract detailed information from a product page and structure it for Excel output"""
        try:
            title_div_holder = soup.find('div', {'class': 'product-title col-lg-8 col-12'})
            title = title_div_holder.find("h1").get_text(strip=True) if title_div_holder else "No Title"

            price_whole = soup.find('span', {'id': 'price-tag'})
            price_fraction = soup.find('sup', {'class': 'after-decimal'})
            price = f"${price_whole.get_text(strip=True)}{price_fraction.get_text(strip=True)}" if price_whole and price_fraction else "N/A"

            product_data = {
                'title': title,
                'price': price,
                'url': product_url
            }

            ul_list = soup.find('ul', {'class': 'tech-specs-list'})
            if ul_list:
                for list in ul_list.find_all('li'):
                    label = list.find("span").get_text(strip=True).lower()
                    value = list.get_text(strip=True)
                    product_data[label] = value

            self._update_gui({"type": "product", 'data': product_data})
            return product_data

        except Exception as e:
            self._update_gui({'type': 'error', 'message': f"Product page error: {str(e)}"})
            return None

    def _construct_page_url(self, base_url, search_term, page):
        # If Ardes uses page numbers directly in URL (like ?page=2)
        return f"{base_url}/products/page/{page}?q={quote(search_term)}"

