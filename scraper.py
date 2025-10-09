import re
from urllib.parse import urljoin, quote
from base_scraper import BaseScraper

class AmazonScraper(BaseScraper):
    def __init__(self, gui_callback=None, driver=None):
        super().__init__(gui_callback, driver)

        self.gpu_keywords = [
            'graphics card', 'gpu', 'video card',
            'rtx', 'gtx', 'radeon', 'geforce',
            'pcie', 'pci-express', 'desktop'
        ]
        self.exclude_keywords = [
            'laptop', 'notebook', 'pc', 'computer', 'system',
            'prebuilt', 'desktop', 'all-in-one', 'mini pc'
        ]

    def _get_base_url(self, search_term):
        """Generate clean search URL without restrictive parameters"""
        encoded_term = quote(search_term)

        return (
            f"https://www.amazon.com/s?k={encoded_term}"
            f"&crid={self.generate_random_crid()}"
            "&ref=nb_sb_noss_1"
        )

    def _extract_product_links(self, soup):
        """Get all product links from a specific search results page URL"""
        product_links = []
        products = soup.find_all('div', {'data-component-type': 's-search-result'})

        for product in products:
            if self.stop_event.is_set():
                break

            if product.find('span', string=re.compile('Sponsored')):
                continue

            link_tag = product.find('a', {'class': 'a-link-normal s-no-outline'})
            if link_tag and 'href' in link_tag.attrs:
                full_url = urljoin('https://www.amazon.com', link_tag['href'])
                clean_url = full_url.split('ref=')[0].split('?')[0]
                if '/dp/' in clean_url and clean_url not in product_links:
                    product_links.append(clean_url)

        return product_links

    def _parse_product_page(self, soup, product_url):
        """Extract detailed information from a product page and structure it for Excel output"""
        try:
            title = soup.find('span', {'id': 'productTitle'})
            title = title.get_text(strip=True) if title else "No Title"

            price_whole = soup.find('span', {'class': 'a-price-whole'})
            price_fraction = soup.find('span', {'class': 'a-price-fraction'})
            price = f"${price_whole.get_text(strip=True)}{price_fraction.get_text(strip=True)}" if price_whole and price_fraction else "N/A"

            product_data = {
                'title': title,
                'price': price,
                'url': product_url
            }

            tech_table = soup.find('table', {'class': 'a-normal a-spacing-micro'})
            if tech_table:
                for row in tech_table.find_all('tr'):
                    tds = row.find_all('td')

                    label = tds[0].get_text(strip=True).lower()
                    value = tds[1].get_text(strip=True)
                    product_data[label] = value

            self._update_gui({"type": "product", 'data': product_data})
            return product_data

        except Exception as e:
            self._update_gui({'type': 'error', 'message': f"Product page error: {str(e)}"})
            return None

    def _construct_page_url(self, base_url, search_term, page):
        if page > 1:
            return f"{base_url}&page={page}"
        return base_url