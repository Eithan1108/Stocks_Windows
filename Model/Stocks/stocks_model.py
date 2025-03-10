# Model/Stocks/stocks_model.py
import requests
import json

class StocksModel:
    def __init__(self):
        self.api_base_url = "http://localhost:5000/api/stocks/prices"
    
    def search_stocks(self, symbol):
        """Search stocks based on the provided symbol"""
        print(f"Searching for stock: {symbol}")
        
        try:
            # Make a post request to the API with the stock name
            response = requests.post(self.api_base_url, json={"tickers": [symbol]})
            
            if response.status_code == 200:
                data = response.json()
                print(f"API response: {json.dumps(data, indent=2)}")
                return data
            else:
                print(f"Error fetching stocks: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Exception during API request: {str(e)}")
            return None