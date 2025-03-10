# main.py
import sys
from PySide6.QtWidgets import QApplication

# Import MVP components
from Model.auth_model import AuthModel
from View.auth_page import LoginWindow
from Presenter.Auth.auth_presenter import AuthPresenter
from Model.Stocks.stocks_model import StocksModel
from View.stock_search_window import StockSearchWindow
from Presenter.Stocks.stocks_presenter import StocksPresenter



def open_stock_search():
    """Create and show the stock search window"""
    stocks_model = StocksModel()
    stock_window = StockSearchWindow()
    stocks_presenter = StocksPresenter(stock_window, stocks_model)
    
    # Show the window
    stock_window.show()
    
    # Return the window reference (to prevent garbage collection)
    return stock_window

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create model, view, and presenter
    auth_model = AuthModel()
    login_window = LoginWindow()
    auth_presenter = AuthPresenter(login_window, auth_model)
    
    # Show login window
    login_window.show()
    
    sys.exit(app.exec())