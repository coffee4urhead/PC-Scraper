from time import sleep, time
from dotenv import load_dotenv
import requests
import os

load_dotenv() 
API_KEY = os.getenv("UNI_RATE_API_KEY")
API_BASE_URL = os.getenv("BASE_URL")

last_api_call = 0
MIN_API_DELAY = 1.0  

def convert_currency(amount, from_currency, to_currency):
    global last_api_call
    
    if from_currency == to_currency:
        print(f"Skipping conversion: same currency {from_currency}")
        return amount
    
    try:
        current_time = time()
        time_since_last_call = current_time - last_api_call
        if time_since_last_call < MIN_API_DELAY:
            sleep_time = MIN_API_DELAY - time_since_last_call
            print(f"Rate limiting: waiting {sleep_time:.2f}s")
            sleep(sleep_time)
        
        url = f"{API_BASE_URL}/convert"
        params = {
            'api_key': API_KEY,
            "from": from_currency,
            "to": to_currency,
            "amount": amount
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  
        
        last_api_call = time()
        
        data = response.json()
        result = data.get("result", amount)
        print(f"Converted {amount} {from_currency} to {result} {to_currency}")
        return result
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print("Rate limit hit! Waiting 5 seconds...")
            sleep(5)
            return amount  
        else:
            print(f"Currency API HTTP error: {e}")
            return amount
    except Exception as e:
        print(f"Currency conversion error: {e}")
        return amount