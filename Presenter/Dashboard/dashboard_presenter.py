# Presenter/Dashboard/dashboard_presenter.py
from event_system import event_system

class DashboardPresenter:
    """Presenter for the dashboard that connects model and view"""
    
    def __init__(self, view, model):
        self.view = view
        self.model = model
        
        # Store reference to dashboard methods without the view knowing about presenter
        self._setup_dashboard_references()
        
        # Connect to global events
        self._connect_events()
    
    def _setup_dashboard_references(self):
        """Store references to important dashboard methods without exposing presenter to view"""
        # Store the method we'll need to call for updates
        self._update_dashboard_data = self.view.update_dashboard_data
        
        # Store user ID for data fetching
        self._user_id = self.view.firebaseUserId
    
    def _connect_events(self):
        """Connect to any global events that should trigger dashboard updates"""
        # Listen for portfolio updates
        event_system.portfolio_updated.connect(self.refresh_dashboard)
        event_system.transactions_updated.connect(self.refresh_dashboard)
    
    def load_initial_data(self):
        """Load initial data for the dashboard"""
        self.refresh_dashboard()
    
    def refresh_dashboard(self):
        """Refresh all dashboard data"""
        # Fetch fresh data from the model
        user_stocks = self.model.get_user_stocks(self._user_id)
        transactions = self.model.get_user_transactions(self._user_id)
        
        # Only fetch stock details if we have stocks
        stocks_details = {}
        if user_stocks:
            stocks_details = self.model.get_stocks_details(user_stocks)
        
        # Update the view with new data
        self._update_dashboard_data(
            user_stocks=user_stocks,
            user_transactions=transactions,
            stocks_the_user_has=stocks_details
        )