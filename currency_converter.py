from dotenv import load_dotenv
import requests
import os

load_dotenv() 
API_KEY = os.getenv("UNI_RATE_API_KEY")
API_BASE_URL = os.getenv("BASE_URL")


def convert_currency(amount, from_currency, to_currency):
    try:
        url = f"{API_BASE_URL}/convert"
        params = {
            'api_key': API_KEY,
            "from": from_currency,
            "to": to_currency,
            "amount": amount
        }
        headers = {
            "Authorization": f"Bearer {API_KEY}" 
        }

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  
        data = response.json()

        return data.get("result", amount)  
    except Exception as e:
        print(f"Currency conversion error: {e}")
        return amount