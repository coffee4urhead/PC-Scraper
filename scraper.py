from urllib.parse import urljoin

import requests
import time
from bs4 import BeautifulSoup
import random

def return_imp_info(search_term):
    base_url = (
        f"https://www.amazon.com/s?k={search_term.replace(' ', '+')}"
        "&crid=32P9R4ODIWA9D"
        "&sprefix=nvidia+rtx+30%2Caps%2C239"
        "&ref=nb_sb_noss_2"
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    return (base_url, headers)


def get_product_links(page_url):
    """Get all product links from a specific search results page URL"""
    product_links = []
    _, headers = return_imp_info("")

    try:
        time.sleep(2 + random.random())
        response = requests.get(page_url, headers=headers)
        response.raise_for_status()

        if "captcha" in response.text.lower():
            print("CAPTCHA detected! Try again later.")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        # Target the specific link structure shown in your HTML
        product_anchors = soup.find_all('a', {
            'class': 'a-link-normal s-line-clamp-2 s-link-style a-text-normal',
            'href': True
        })

        for anchor in product_anchors:
            # Skip sponsored products by checking parent hierarchy
            if anchor.find_parent('div', {'data-component-type': 's-sponsored-result'}):
                continue

            full_url = urljoin('https://www.amazon.com', anchor['href'])

            # Clean URL by:
            # 1. Removing ref parameter
            # 2. Keeping only the product ID portion
            clean_url = full_url.split('ref=')[0].split('?')[0]

            # Only keep URLs that contain '/dp/' (product pages)
            if '/dp/' in clean_url:
                product_links.append(clean_url)

        return product_links

    except Exception as e:
        print(f"Error getting product links from {page_url}: {e}")
        return []


def get_product_details(product_url):
    """Extract detailed information from a product page"""
    try:
        response = requests.get(product_url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    })
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract product title
        title = soup.find('span', {'id': 'productTitle'}).get_text(strip=True)

        # Extract price (handling different price formats)
        price_whole = soup.find('span', {'class': 'a-price-whole'}).get_text(strip=True)
        price_fraction = soup.find('span', {'class': 'a-price-fraction'}).get_text(strip=True)
        price_symbol = soup.find('span', {'class': 'a-price-symbol'}).get_text(strip=True)

        final_price = f"{price_symbol}{price_whole}.{price_fraction}"
        # Extract technical details from the table
        tech_details = {}
        tech_table = soup.find('table', {'class': ['a-normal', 'a-spacing-micro']})
        if tech_table:
            for row in tech_table.find_all('tr'):
                th = row.find('th')
                td = row.find('td')
                if th and td:
                    tech_details[th.get_text(strip=True)] = td.get_text(strip=True)

        return {
            'title': title,
            'price': final_price,
            'url': product_url,
            'technical_details': tech_details,
        }

    except Exception as e:
        print(f"Error scraping product page {product_url}: {e}")
        return None


def begin_scraping(search_term, max_pages=3):
    """Main scraping function that uses all helper methods"""
    current_page = 1
    all_products = []
    has_next_page = True

    # Keywords for filtering physical GPUs
    gpu_keywords = [
        'graphics card', 'gpu', 'video card',
        'rtx', 'gtx', 'radeon', 'geforce',
        'pcie', 'pci-express', 'desktop'
    ]

    exclude_keywords = [
        'laptop', 'notebook', 'pc', 'computer', 'system',
        'prebuilt', 'desktop', 'all-in-one', 'mini pc'
    ]
    base_url, headers = return_imp_info(search_term)

    while has_next_page and current_page <= max_pages:
        print(f"\nScraping page {current_page}...")

        # Get base URL and headers for this search term
        page_url = f"{base_url}&page={current_page}"

        try:
            # Get all product links from the page using your existing method
            product_links = get_product_links(page_url)

            if not product_links:
                print(f"No products found on page {current_page}")
                break

            # Process each product link
            for product_url in product_links:
                try:
                    # Get basic product info first (fast)
                    time.sleep(1 + random.random())
                    response = requests.get(product_url, headers=headers)
                    if "captcha" in response.text.lower():
                        print("CAPTCHA detected! Stopping scraping.")
                        return all_products

                    soup = BeautifulSoup(response.text, 'html.parser')
                    title = soup.find('span', {'id': 'productTitle'})
                    title_text = title.get_text(strip=True).lower() if title else ""

                    # Check if this is a physical GPU
                    is_gpu = any(keyword in title_text for keyword in gpu_keywords)
                    is_not_gpu = any(keyword in title_text for keyword in exclude_keywords)

                    if not is_gpu or is_not_gpu:
                        continue  # Skip non-GPU products

                    # Now get full details using your existing method
                    time.sleep(2 + random.random())  # Additional delay for detail pages
                    product_details = get_product_details(product_url)

                    if product_details:
                        # Add additional fields you want
                        product_details['search_term'] = search_term
                        product_details['page_number'] = current_page

                        # Get rating if not already in details
                        if 'rating' not in product_details:
                            rating = soup.find('span', class_='a-icon-alt')
                            product_details['rating'] = rating.get_text().split()[0] if rating else 'N/A'

                        all_products.append(product_details)
                        print(f"✔ GPU Found: {product_details['title']} | Price: {product_details.get('price', 'N/A')}")

                except Exception as e:
                    print(f"Error processing product {product_url}: {e}")
                    continue

            # Check for next page
            next_page_url = f"{base_url}&page={current_page + 1}"
            test_response = requests.get(next_page_url, headers=headers)
            has_next_page = "Sorry, we couldn't find that page" not in test_response.text

        except Exception as e:
            print(f"Error scraping page {current_page}: {e}")
            break

        current_page += 1
        time.sleep(3 + random.random())  # Delay between pages

    return all_products