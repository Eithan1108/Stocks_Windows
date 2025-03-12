import requests

class PortfolioModel:
    def __init__(self):
        pass

    def sell_stock(self, symbol, quantity, firebaseUserId):
        """Sell a stock from the portfolio"""
        print(f"Selling {quantity} shares of {symbol} now in the model")

        response = requests.post("http://localhost:5000/api/stocks/sell", json={
            "firebaseUserId": firebaseUserId,
            "stockSymbol": symbol,
            "quantity": quantity
        })
        print("Response in model:", response.text)
        if response.status_code == 200:
            print("Stock sold successfully")
            return True
        else:
            print("Failed to sell stock")
            return False
    
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
        
        api = APIService()
        return api.get_user_transactions(user_id)
    
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
