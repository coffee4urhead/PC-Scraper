from time import sleep, time
from dotenv import load_dotenv
import requests
import os

load_dotenv() 
API_KEY = os.getenv("UNI_RATE_API_KEY")
API_BASE_URL = os.getenv("BASE_URL")

last_api_call = 0
MIN_API_DELAY = 2.0  

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
        
        print(f"🔧 API CALL: {from_currency} -> {to_currency}, amount: {amount}")
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()  
        
        last_api_call = time()
        
        result = data.get("result")
        if result is None:
            print(f"❌ API returned no result")
            return None
            
        print(f"✅ Converted {amount} {from_currency} to {result} {to_currency}")
        return result
        
    except Exception as e:
        print(f"❌ Conversion error: {e}")
        return None