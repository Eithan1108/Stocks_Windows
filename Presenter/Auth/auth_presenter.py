# Presenters/Auth/auth_presenter.py
from Model.auth_model import AuthModel
from View.auth_page import LoginPage
from View.home_page import MainWindow
from PySide6.QtWidgets import QPushButton, QLineEdit  # Change PyQt5 to PySide6
from PySide6.QtCore import Slot
from Google_Auth.google_auth import GoogleAuthService
from PySide6.QtCore import Slot, QTimer
import os

try:
    from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
except ImportError:
    # Use environment variables if config file doesn't exist
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")

class AuthPresenter:
    def __init__(self, view, model):
        self.view = view
        self.model = model

        # Initialize Google Auth Service with credentials from config/environment
        self.google_auth_service = GoogleAuthService(
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET
        )
        
        # Connect Google Auth signals
        self.google_auth_service.auth_success.connect(self.handle_google_auth_success)
        self.google_auth_service.auth_failure.connect(self.handle_google_auth_failure)
        
        # Connect view signals to presenter methods
        self.connect_signals()
        self.view.init_loading_overlay()

    def connect_signals(self):
        """Connect UI signals to presenter methods"""
        if hasattr(self.view, 'stacked_widget'):
            login_page = self.view.stacked_widget.widget(0)
        else:
            login_page = self.view
        
        # Connect to the login button more directly
        login_btn = login_page.get_login_button()
        signup_btn = login_page.get_signup_button()
        google_login_btn = login_page.get_google_login_button()
        google_signup_btn = login_page.get_google_signup_button()

        if login_btn:
            login_btn.clicked.connect(self.handle_login)
        if signup_btn:
            signup_btn.clicked.connect(self.handle_signup)
        if google_login_btn:
            google_login_btn.clicked.connect(self.handle_google_login)
        if google_signup_btn:
            google_signup_btn.clicked.connect(self.handle_google_login)

    def handle_login(self):
        """Handle login button click"""
        # Get the login page
        if hasattr(self.view, 'stacked_widget'):
            login_page = self.view.stacked_widget.widget(0)
        else:
            login_page = self.view
        
        # Get credentials using the accessor method
        email, password = login_page.get_login_credentials()
        
        # Show loading overlay
        self.view.loading_overlay.start("Logging in...")
        
        # Simulate network delay for demonstration
        # In a real app, you'd perform actual authentication here
        QTimer.singleShot(1500, lambda: self._complete_login(email, password))
    
    def _complete_login(self, email, password):
        """Complete the login process after delay/authentication"""
        # Call model method
        success, message, text = self.model.validate_login(email, password)
        
        # Update UI based on result
        if success:
            # Keep showing loading while transitioning to home screen
            self.view.loading_overlay.message_label.setText("Loading your dashboard...")
            QTimer.singleShot(1000, lambda: self.view.navigate_to_home(email))
        else:
            # Stop loading and show error
            self.view.loading_overlay.stop()
            self.view.show_input_error(message, text)
    
    def handle_signup(self):
        """Handle signup button click"""
        if hasattr(self.view, 'stacked_widget'):
            login_page = self.view.stacked_widget.widget(0)
        else:
            login_page = self.view
        
        name, email, password, confirm_password, terms_accepted = login_page.get_signup_credentials()

        # Show loading overlay
        self.view.loading_overlay.start("Creating your account...")
        
        # Simulate network delay for demonstration
        QTimer.singleShot(2000, lambda: self._complete_signup(name, email, password, confirm_password, terms_accepted))
    
    def _complete_signup(self, name, email, password, confirm_password, terms_accepted):
        """Complete the signup process after delay/authentication"""
        # Call model method
        success, message, text = self.model.validate_signup(name, email, password, confirm_password, terms_accepted)

        # Update UI based on result
        if success:
            # Keep showing loading while transitioning to home screen
            self.view.loading_overlay.message_label.setText("Setting up your account...")
            QTimer.singleShot(1000, lambda: self.view.navigate_to_home(email))
        else:
            # Stop loading and show error
            self.view.loading_overlay.stop()
            self.view.show_signup_input_error(message, text)
        
        
    def handle_forgot_password(self):
        """Handle forgot password button click"""
        # Similar logic for password reset
        pass

    def handle_google_login(self):
        """Handle Google login button click"""
        # Show a loading indicator or message
        # self.view.show_info_message("Google Sign-In", "Opening Google sign-in page...")
        self.view.loading_overlay.start("Connecting to Google...")
        
        # Start the Google authentication flow
        self.google_auth_service.start_auth_flow()
    
    @Slot(str)
    def handle_google_auth_success(self, id_token):
        """Handle successful Google authentication"""
        print("Google login successful with token:", id_token)
        
        # Update loading message
        self.view.loading_overlay.message_label.setText("Verifying your Google account...")
        
        # Call the model to validate the Google token with the backend
        success, message, user_data = self.model.login_with_google(id_token)
        
        if success:
            # Get email from user data or use a default
            email = user_data.get("email", "Google User")
            print("Google login successful for:", email)
            
            # Update loading message for transition
            self.view.loading_overlay.message_label.setText("Loading your dashboard...")
            
            # Use timer to allow the UI to update before navigation
            QTimer.singleShot(800, lambda: self.view.navigate_to_home(email))
        else:
            # Stop loading and show error
            self.view.loading_overlay.stop()
            self.view.show_error_message("Google Sign-In Error", message)

    @Slot(str)
    def handle_google_auth_failure(self, error_message):
        """Handle Google authentication failure"""
        # Always stop the loading overlay
        if hasattr(self.view, 'loading_overlay') and self.view.loading_overlay:
            self.view.loading_overlay.stop()
        
        # Only show error message for real errors, not cancellations
        if "cancelled" not in error_message.lower() and "timed out" not in error_message.lower():
            self.view.show_error_message("Google Sign-In Error", error_message)
        else:
            print(f"Google auth ended: {error_message}")
    
    def handle_forgot_password(self):
        """Handle forgot password button click"""
        # This will be implemented later
        pass