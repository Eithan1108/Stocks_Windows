# Presenters/Auth/auth_presenter.py
from Model.auth_model import AuthModel
from View.auth_page import LoginPage
from View.home_page import MainWindow
from PySide6.QtWidgets import QPushButton, QLineEdit  # Change PyQt5 to PySide6

class AuthPresenter:
    def __init__(self, view, model):
        self.view = view
        self.model = model
        
        # Connect view signals to presenter methods
        self.connect_signals()

    def connect_signals(self):
        """Connect UI signals to presenter methods"""
        if hasattr(self.view, 'stacked_widget'):
            login_page = self.view.stacked_widget.widget(0)
        else:
            login_page = self.view
        
        # Connect to the login button more directly
        login_btn = login_page.get_login_button()
        signup_btn = login_page.get_signup_button()
        if login_btn:
            login_btn.clicked.connect(self.handle_login)
        if signup_btn:
            signup_btn.clicked.connect(self.handle_signup)

    def handle_login(self):
        """Handle login button click"""
        # Get the login page
        if hasattr(self.view, 'stacked_widget'):
            login_page = self.view.stacked_widget.widget(0)
        else:
            login_page = self.view
        
        # Get credentials using the accessor method
        email, password = login_page.get_login_credentials()
        
        # Call model method
        success, message, text = self.model.validate_login(email, password)
        
        # Update UI based on result
        if success:
            # Navigate to home with user data
            self.view.navigate_to_home(email)
        else:
            # Show error
            self.view.show_input_error(message, text)
    
    def handle_signup(self):
        """Handle signup button click"""
        if hasattr(self.view, 'stacked_widget'):
            login_page = self.view.stacked_widget.widget(0)
        else:
            login_page = self.view
        
        name, email, password, confirm_password, terms_accepted = login_page.get_signup_credentials()

        # Call model method
        success, message, text = self.model.validate_signup(name, email, password, confirm_password, terms_accepted)

        # Update UI based on result
        if success:
            # Show success message
            self.view.navigate_to_home(email)
        else:
            # Show error
            self.view.show_signup_input_error(message, text)
        
    
    def handle_forgot_password(self):
        """Handle forgot password button click"""
        # Similar logic for password reset
        pass