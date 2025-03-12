from View.protofilio_view import StocksListWidget  # Replace 'some_module' with the actual module name
from View.protofilio_view import StockItem
from View.protofilio_view import PortfolioCard
from event_system import event_system

class PortfolioPresenter:
    def __init__(self, view, model):
        self.view = view
        self.model = model
        self.view.set_presenter(self)
        self.current_stock_dialogs = {}  # Track open dialogs
        
        # Connect to stock items in the view
        self.setup_stock_item_connections()
        self._connect_events()
    
    def _connect_events(self):
        """Connect to any global events that should trigger portfolio updates"""
        # Listen for portfolio and transaction updates
        event_system.portfolio_updated.connect(self.refresh_portfolio)
        event_system.transactions_updated.connect(self.refresh_portfolio)

    def refresh_portfolio(self):
        """Refresh all portfolio data"""
        if not hasattr(self.view, 'firebaseUserId') or not self.view.firebaseUserId:
            return
            
        # Fetch fresh data from the model
        user_stocks = self.model.get_user_stocks(self.view.firebaseUserId)
        balance = self.model.get_user_balance(self.view.firebaseUserId)
        
        # Only fetch stock details if we have stocks
        stocks_details = {}
        if user_stocks:
            stocks_details = self.model.get_stocks_details(user_stocks)
        
        # Update the view's data
        self.view.user_stocks = user_stocks
        self.view.stocks_the_user_has = stocks_details
        self.view.balance = balance
        
        # Update the UI
        self.view.update_after_transaction()

    def setup_stock_item_connections(self):
        """Connect to stock items to access their sell buttons"""
        if hasattr(self.view, 'details_section'):
            for stock_item in self.get_stock_items():
                stock_item.register_presenter(self)
    
    def get_stock_items(self):
        """Get all stock items from the view"""
        stock_items = []
        
        # First, try to find the stocks list widget
        try:
            # Navigate through the view hierarchy to find StockItem widgets
            for i in range(self.view.details_section_layout.count()):
                widget = self.view.details_section_layout.itemAt(i).widget()
                if isinstance(widget, PortfolioCard):
                    # Find the StocksListWidget inside the card
                    stocks_list = None
                    for j in range(widget.layout.count()):
                        child_widget = widget.layout.itemAt(j).widget()
                        if isinstance(child_widget, StocksListWidget):
                            stocks_list = child_widget
                            break
                    
                    if stocks_list:
                        # Get the container within the scroll area
                        container = stocks_list.widget()
                        # Get all stock items from the container's layout
                        container_layout = container.layout()
                        for k in range(container_layout.count()):
                            item = container_layout.itemAt(k)
                            if item and item.widget() and isinstance(item.widget(), StockItem):
                                stock_items.append(item.widget())
        except (AttributeError, IndexError) as e:
            print(f"Error finding stock items: {e}")
        
        return stock_items
        
    def get_active_sell_dialog(self):
        """Find any stock item that has an open sell dialog"""
        for stock_item in self.get_stock_items():
            if stock_item.sell_dialog is not None:
                return stock_item
        return None
    
    def on_stock_dialog_opened(self, stock_item):
        """Called when a stock item opens its dialog"""
        print(f"Dialog opened for {stock_item.get_stock_symbol()}")
        self.current_stock_dialogs[stock_item] = True
        
        # Connect the sell button
        if stock_item.sell_btn:
            print("Connecting sell button")
            # Disconnect any existing connections first (safety measure)
            try:
                stock_item.sell_btn.clicked.disconnect()
            except:
                pass
                
            # Connect to our handler
            stock_item.sell_btn.clicked.connect(
                lambda: self.handle_sell_button_click(stock_item)
            )

    def on_stock_dialog_closed(self, stock_item):
            """Called when a stock item closes its dialog"""
            print(f"Dialog closed for {stock_item.get_stock_symbol()}")
            if stock_item in self.current_stock_dialogs:
                del self.current_stock_dialogs[stock_item]


    def handle_sell_button_click(self, stock_item):
        """Handle sell button click from a stock item"""
        print("Sell button clicked")
        
        if not stock_item:
            print("No stock item provided")
            return False
        
        quantity = stock_item.get_quantity()
        if quantity is None:
            print("No quantity available")
            return False
            
        symbol = stock_item.get_stock_symbol()
        price = stock_item.stock_data.get("price", 0)

        print(f"Selling {quantity} shares of {symbol} at {price}")
        
        # Here you would implement your selling logic
        success = self.model.sell_stock(symbol, quantity, self.view.firebaseUserId)


        
        if success:
            print("Sell successful, getting updated data...")
            # Close the dialog
            if stock_item.sell_dialog:
                stock_item.sell_dialog.close()

            user_id = self.view.firebaseUserId
            user_stocks = self.model.get_user_stocks(user_id)
            transactions = self.model.get_user_transactions(user_id)
            stocks_details = self.model.get_stocks_details(user_stocks)

            print("Emitting data_updated signal...")

            
            event_system.portfolio_updated.emit()
            event_system.transactions_updated.emit()
            event_system.data_updated.emit(user_stocks, transactions, stocks_details)
            
            
            return True
        return False