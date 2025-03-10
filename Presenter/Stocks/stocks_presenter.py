# Presenter/Stocks/stocks_presenter.py
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
        else:
            self.view.initial_message.setVisible(False)
            self.view.no_results_message.setVisible(True)

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
    