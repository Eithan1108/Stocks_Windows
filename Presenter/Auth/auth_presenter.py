# Presenters/Auth/auth_presenter.py
from Model.auth_model import AuthModel
from View.auth_page import LoginPage
from View.home_page import MainWindow
from PyQt5.QtWidgets import QPushButton, QLineEdit

class AuthPresenter:
    def __init__(self, view, model):
        self.view = view
        self.model = model
        
        # Connect view signals to presenter methods
        self.connect_signals()
    
    # In auth_presenter.py
    def connect_signals(self):
        """Connect UI signals to presenter methods"""
        # Check if view is LoginWindow, and get the login_page if needed
        if hasattr(self.view, 'stacked_widget'):
            # If we're using the LoginWindow, get the LoginPage from it
            login_page = self.view.stacked_widget.widget(0)
        else:
            # We already have the LoginPage
            login_page = self.view
        
        # Now find the button within the correct page
        login_btn = login_page.findChild(QPushButton, "login_btn")
        
        # Debug print to check if we found the button
        print(f"Login button found: {login_btn is not None}")
        
        if login_btn:
            login_btn.clicked.connect(self.handle_login)
        else:
            print("WARNING: Could not find login button")
    
    def handle_login(self):
        """Handle login button click"""
        # Get inputs
        email_input = self.view.findChild(QLineEdit, "email_input")
        password_input = self.view.findChild(QLineEdit, "password_input")
        
        email = email_input.text()
        password = password_input.text()
        
        # Call model method
        success, message = self.model.validate_login(email, password)
        
        # Tell the View what to do based on the result
        if success:
            # Just tell the view to navigate to the home screen
            self.view.navigate_to_home(email)
        else:
            # Tell the view to show an error
            self.view.show_error_message("Login Error", message)
    
    def handle_signup(self):
        """Handle signup button click"""
        # Similar logic for signup
        pass
    
    def handle_forgot_password(self):
        """Handle forgot password button click"""
        # Similar logic for password reset
        pass