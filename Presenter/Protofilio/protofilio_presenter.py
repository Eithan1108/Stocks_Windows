from View.protofilio_view import StocksListWidget  # Replace 'some_module' with the actual module name
from View.protofilio_view import StockItem
from View.protofilio_view import PortfolioCard

class PortfolioPresenter:
    def __init__(self, view, model):
        self.view = view
        self.model = model
        self.view.set_presenter(self)
        self.current_stock_dialogs = {}  # Track open dialogs
        
        # Connect to stock items in the view
        self.setup_stock_item_connections()
    
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
            # Close the dialog
            if stock_item.sell_dialog:
                stock_item.sell_dialog.close()
                
            # Update the view
            self.view.update_after_transaction()
            return True
        return False