# Model/Stocks/stocks_model.py
import requests
import json
from datetime import timedelta

class StocksModel:
    def __init__(self):
        self.api_base_url = "http://localhost:5000/api/stocks/prices"
    
    def search_stocks(self, symbol, now_date):
        """Search stocks based on the provided symbol"""
        print(f"Searching for stock: {symbol}")
        
        try:
            # Make a post request to the API with the stock name
            response = requests.post(self.api_base_url, json={"tickers": [symbol]})
            
            if response.status_code == 200:
                data = response.json()
                history = self.get_stock_history(symbol, now_date)
                print(f"API response: {json.dumps(data, indent=2)}")
                return data, history
            else:
                print(f"Error fetching stocks: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Exception during API request: {str(e)}")
            return None
        
    def search_stocks_by_name(self, name, now_date):
        """Search stocks based on the provided symbol"""
        print(f"Searching for stock: {name}")
        
        try:
            # Make a post request to the API with the stock name
            response = requests.get("http://localhost:5000/api/stocks/search?query="+name)
            
            if response.status_code == 200:
                data = response.json()
                print(f"API response from search_stocks_by_name: {response}")
                # Gets the symbol from this {"symbol":"AAPL"} and calls the search_stocks function
                symbol = data.get("symbol")
                response = requests.post(self.api_base_url, json={"tickers": [symbol]})
                history = self.get_stock_history(symbol, now_date)
                data = response.json()
                return data, history
            else:
                print(f"Error fetching stocks: {response}")
                return None
                
        except Exception as e:
            print(f"Exception during API request: {str(e)}")
            return None

    def buy_stock(self, symbol, quantity, firebaseId):
        """Buy a stock based on the provided symbol and quantity"""
        print(f"Buying stock: {symbol}, Quantity: {quantity}")
        
        try:
            # Make a post request to the API with the stock name and quantity
            response = requests.post("http://localhost:5000/api/stocks/buy", json={
                "firebaseUserId": firebaseId,
                "stockSymbol": symbol,
                "quantity": int(quantity)
                })
            
            if response.status_code == 200:
                data = response.json()
                print(f"API response: {json.dumps(data, indent=2)}")
                return data
            else:
                print(f"Error buying stock: {response.json()}")
                return None
                
        except Exception as e:
            print(f"Exception during API request: {str(e)}")
            return None
        
    def get_user_stocks(self, user_id):
        """Get user stocks from database/API"""
        """Get user's stock portfolio from the API"""
        try:
            
            response = requests.get("http://localhost:5000/api/user/" + user_id + "/stocks")
            if response.status_code == 200:
                stocks_data = response.json()
                return stocks_data
            else:
                return None
        except Exception as e:
            print(f"API request error: {e}")
            return None
        
        api = APIService()
        return api.get_user_stocks(user_id)
    
    def get_user_transactions(self, user_id):
        """Get user's transaction history from the API"""
        try:
            
            response = requests.get("http://localhost:5000/api/user/" + user_id + "/transactions")
            if response.status_code == 200:
                transactions_data = response.json()
                return transactions_data
            else:
                return None
        except Exception as e:
            print(f"API request error: {e}")
            return None

    
    def get_stocks_details(self, user_stocks):
        print(f"Searching for stock: {user_stocks}")

        # Get the stocks symbols from [{'stockSymbol': 'AAPL', 'quantity': 30}, {'stockSymbol': 'AMZN', 'quantity': 12}, {'stockSymbol': 'AA', 'quantity': 1}, {'stockSymbol': 'ABCB', 'quantity': 12}, {'stockSymbol': 'APH', 'quantity': 11}, {'stockSymbol': 'ASLE', 'quantity': 38}]
        stocks = [stock['stockSymbol'] for stock in user_stocks]

        try:
            # Make a post request to the API with the stock name
            
            response = requests.post("http://localhost:5000/api/stocks/prices", json={"tickers": stocks})
            
            if response.status_code == 200:
                data = response.json()
                print(f"API response for get_stocks_user_holds in the model: {data}")
                return data
            else:
                print(f"Error fetching stocks in dahs: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Exception during API request: {str(e)}")
            return None
        
    def get_user_balance(self, firebase_id):
        """Get the current balance for a user"""
        try:
            import requests
            response = requests.get(f"{self.api_base_url}/user/balance/{firebase_id}")
            if response.status_code == 200:
                data = response.json()
                return data.get("balance")
            else:
                print(f"Failed to get balance. Status code: {response.status_code}")
                # Return dummy balance for testing
                return 500.00
        except Exception as e:
            print(f"Error fetching balance: {str(e)}")
            # Return dummy balance for testing
            return 500.00
        

    def get_stock_history(self, symbol, now_date):
        """Get historical data for a stock"""
        last_week = "1-1-2025"
        # Format to YYYY-MM-DD
        now_date_str = now_date.strftime("%Y-%m-%d")
        try:
            response = requests.get(f"http://localhost:5000/api/stocks/history?ticker={symbol}&startDate={last_week}&endDate={now_date_str}")
            if response.status_code == 200:
                data = response.json()
                print(f"API response for get_stock_history: {data}")
                return data
            else:
                print(f"Failed to get stock history. Status code: {response}")
                return None
        except Exception as e:
            print(f"Error fetching stock history: {str(e)}")
            return