import yfinance as yf
import requests
from datetime import datetime, timedelta

class RealCurrencyConverter:
    def __init__(self):
        self.rates_cache = {}
        self.cache_time = None
        self.cache_duration = 3600  
        
    def get_real_time_rate(self, from_currency, to_currency):
        """Get real-time rate with fallback sources"""
        if from_currency == to_currency:
            return 1.0
        
        cache_key = f"{from_currency}_{to_currency}"

        if (cache_key in self.rates_cache and 
            self.cache_time and 
            (datetime.now() - self.cache_time).seconds < self.cache_duration):
            return self.rates_cache[cache_key]

        rate = self._get_yahoo_rate(from_currency, to_currency)
        if rate:
            self.rates_cache[cache_key] = rate
            self.cache_time = datetime.now()
            return rate
        
        rate = self._get_exchangerate_api(from_currency, to_currency)
        if rate:
            self.rates_cache[cache_key] = rate
            self.cache_time = datetime.now()
            return rate
        
        rate = self._get_fallback_rate(from_currency, to_currency)
        if rate:
            print(f"⚠️ Using fallback rate (may be outdated)")
            return rate
        
        return None
    
    def _get_yahoo_rate(self, from_currency, to_currency):
        """Get rate from Yahoo Finance"""
        try:
            ticker = f"{from_currency}{to_currency}=X"
            data = yf.download(ticker, period="1d", progress=False)
            
            if not data.empty:
                rate = data['Close'].iloc[-1]
                print(f"📊 Yahoo Finance {from_currency}/{to_currency}: {rate:.4f}")
                return rate
        except Exception as e:
            print(f"Yahoo Finance failed: {e}")
        return None
    
    def _get_exchangerate_api(self, from_currency, to_currency):
        """Get rate from ExchangeRate-API"""
        try:
            url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
            response = requests.get(url, timeout=10)
            data = response.json()
            rate = data['rates'][to_currency]
            print(f"📊 ExchangeRate-API {from_currency}/{to_currency}: {rate:.4f}")
            return rate
        except:
            return None

    def convert_currency(self, amount, from_currency, to_currency):
        """Convert currency with real-time rates"""
        rate = self.get_real_time_rate(from_currency, to_currency)
        if rate:
            converted = amount * rate
            print(f"✅ Converted {amount} {from_currency} to {converted:.2f} {to_currency}")
            return converted
        return None