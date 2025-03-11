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
        
