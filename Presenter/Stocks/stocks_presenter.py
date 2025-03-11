# Modified StocksPresenter class with dialog handling fixes
from event_system import event_system

class StocksPresenter:
    def __init__(self, view, model):
        self.view = view
        self.model = model
        self.view.set_presenter(self)
        
        # Connect view signals to presenter methods
        self.connect_signals()

    def connect_signals(self):
        """Connect UI signals to presenter methods"""
        search_btn = self.view.get_search_button()
        if search_btn:
            # Ensure the presenter is kept alive with the button
            self._search_btn = search_btn
            # Disconnect any existing connections first
            try:
                self._search_btn.clicked.disconnect()
            except:
                pass
            # Connect to our handler
            self._search_btn.clicked.connect(self.handle_search)
            print("Connected search button to handle_search method")

    def handle_search(self):
        print("Search button clicked - handler called!")
        search_text = self.view.get_search_text()
        
        # Clear previous results
        self.view._clear_results()
        
        # Show appropriate message if search is empty
        if not search_text:
            self.view.initial_message.setVisible(True)
            self.view.no_results_message.setVisible(False)
            return
            
        # Get results from model
        api_results = self.model.search_stocks(search_text)
        
        if not api_results:
            self.view.initial_message.setVisible(False)
            self.view.no_results_message.setVisible(True)
            return
        
        # Convert API response to format expected by the view
        formatted_results = self.format_stock_data(api_results)
        
        # Display results or no results message
        if formatted_results:
            self.view._show_search_results(formatted_results)
            self.view.initial_message.setVisible(False)
            self.view.no_results_message.setVisible(False)
            
            # Connect buy button after displaying results
            self.connect_buy_button()
        else:
            self.view.initial_message.setVisible(False)
            self.view.no_results_message.setVisible(True)

    def connect_buy_button(self):
        """Connect buy button to handler"""
        buy_button = self.view.get_buy_button()
        stock_card = self.view.stock_card
        
        if buy_button:
            # Disconnect any existing connections first
            try:
                buy_button.clicked.disconnect(self.on_buy_clicked)
            except:
                pass
            buy_button.clicked.connect(self.on_buy_clicked)
            print("Connected buy button to handler")
        
        # Connect to the dialog_created signal
        if stock_card:
            # Disconnect any existing connections to avoid duplications
            try:
                stock_card.dialog_created.disconnect(self.on_dialog_created)
            except:
                pass
            stock_card.dialog_created.connect(self.on_dialog_created)
            print("Connected to dialog_created signal")

    def on_buy_clicked(self):
        """Handle buy button click"""
        print("Buy button clicked - waiting for dialog creation signal")
        # The actual connection to the dialog happens via the dialog_created signal
    
    def on_dialog_created(self, dialog):
        """Handle when a dialog is created"""
        print("Dialog created - connecting to confirm button")
        if dialog and dialog.confirm_btn:
            # Disconnect any existing connections first
            try:
                dialog.confirm_btn.clicked.disconnect(self.on_confirm_clicked)
            except:
                pass
            dialog.confirm_btn.clicked.connect(self.on_confirm_clicked)
            print("Connected confirm button to handler")
    
    def on_confirm_clicked(self):
        """Handle confirm button click"""
        dialog = self.view.stock_card.purchase_dialog
        symbol = dialog.stock_data["symbol"]
        quantity = dialog.quantity_input.value()
        print("Purchase confirmation button clicked!")
        self.model.buy_stock(symbol, quantity, self.view.firebaseId)
        event_system.portfolio_updated.emit()

        # Your purchase logic here

    def format_stock_data(self, api_results):
        """Format API response data to match the format expected by StockInfoCard"""
        formatted_stocks = []
        
        for symbol, stock_data in api_results.items():
            # Calculate or extract necessary values
            current_price = stock_data.get("currentPrice", 0)
            open_price = stock_data.get("openPrice", 0)
            high_price = stock_data.get("highPrice", 0)
            low_price = stock_data.get("lowPrice", 0)
            prev_close = stock_data.get("previousClose", 0)
            change_percent = stock_data.get("changePercent", 0)
            company_name = stock_data.get("name", "")
            volume = stock_data.get("volume", 0)
            yearLow = stock_data.get("yearLow", 0)
            yearHigh = stock_data.get("yearHigh", 0)
            pe = stock_data.get("pe", 0)
            eps = stock_data.get("eps", 0)
            dividend = stock_data.get("dividend", 0)
            
            # Format market cap 
            market_cap = "$198.5B"  # Default value

            # Format stock data for the view
            formatted_stock = {
                "symbol": symbol,
                "name": company_name,
                "price": round(current_price, 2),
                "change": round(change_percent, 2),
                "open": round(open_price, 2),
                "prevClose": round(prev_close, 2),
                "volume": volume,
                "dayLow": round(low_price, 2),
                "dayHigh": round(high_price, 2),
                "yearLow": yearLow,
                "yearHigh": yearHigh,
                "marketCap": market_cap,
                "pe": pe,
                "eps": eps,
                "dividend": dividend
            }
            
            formatted_stocks.append(formatted_stock)
            
        return formatted_stocks