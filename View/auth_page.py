import sys
import os
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
                               QLineEdit, QPushButton, QStackedWidget, QFrame,
                               QCheckBox, QMessageBox)
from PySide6.QtGui import (QColor, QFont, QPainter, QPixmap, QPen, QLinearGradient, QMovie,
                           QBrush, QIcon)
from PySide6.QtCore import Qt, QSize, QRect, Signal, QTimer
# In auth_page.py
from View.shared_components import ColorPalette, GlobalStyle, AvatarWidget
from PySide6.QtCore import QObject, QEvent
from PySide6.QtGui import QImage, QPainter, QColor, QPen, QBrush
from PySide6.QtCore import Qt, QRect
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, Signal, QSize, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QColor, QPainter, QPen, QBrush
from View.loading_overlay import LoadingOverlay



class SocialLoginButton(QPushButton):
    """Custom social login button with icon and styling"""
    def __init__(self, icon_path, text, color, provider=None):
        super().__init__(text)
        self.provider = provider

        # Button styling
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {color}E6;  /* Slightly darker on hover */
            }}
        """)

        # Set icon
        try:
            icon = QIcon(icon_path)
            self.setIcon(icon)
        except Exception as e:
            print(f"Could not load icon: {e}")

        self.setIconSize(QSize(24, 24))

        # Ensure icon is on the left
        self.setLayoutDirection(Qt.LeftToRight)


class AuthenticationManager:
    @staticmethod
    def validate_login(email, password):
        print(f"Validating login: {email}, {password}")  # Debug print
        """
        Validate login credentials
        """
        # Check if email and password are not empty
        if not email or not password:
            return False

        # Check for valid email format (contains @ and .)
        if '@' not in email or '.' not in email:
            return False

        # Check minimum password length
        if len(password) < 8:
            return False

        # You can add more complex validation here
        return True

    @staticmethod
    def validate_signup(name, email, password, confirm_password, terms_accepted):
        """
        Validate signup information
        """
        # Basic validation checks
        if not name:
            return False, "Name cannot be empty"

        if not email or '@' not in email:
            return False, "Invalid email address"

        if len(password) < 8:
            return False, "Password must be at least 8 characters"

        if password != confirm_password:
            return False, "Passwords do not match"

        if not terms_accepted:
            return False, "You must accept the terms and conditions"

        return True, "Signup successful"

    @staticmethod
    def reset_password(email):
        """
        Handle password reset logic
        """
        if not email or '@' not in email:
            return False, "Invalid email address"

        return True, "Password reset link sent to your email"

class LoginPage(QWidget):

    login_requested = Signal(str, str)  # email, password
    signup_requested = Signal(str, str, str, str, bool)  # name, email, password, confirm_password, terms_accepted
    forgot_password_requested = Signal(str)  # email

    def __init__(self, parent=None):

        super().__init__(parent)

        # Set up main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Left side - Branding
        left_side = self._create_left_side()

        # Right side - Login Forms
        right_side = self._create_right_side()

        # Add sides to main layout
        main_layout.addWidget(left_side, 1)
        main_layout.addWidget(right_side, 1)

    # Add these methods to make UI elements easier to access
    def get_login_button(self):
        return self.findChild(QPushButton, "login_btn")
    
    def get_signup_button(self):
        return self.findChild(QPushButton, "signup_btn")
    
    def get_google_login_button(self):
        return self.findChild(QPushButton, "google_login_btn")
    
    def get_google_signup_button(self):
        return self.findChild(QPushButton, "google_signup_btn")

    def get_login_credentials(self):
        email = self.findChild(QLineEdit, "email_input").text()
        password = self.findChild(QLineEdit, "password_input").text()
        return email, password

    # Add methods for the presenter to call

        QMessageBox.warning(self, title, message)

    def get_signup_credentials(self):
        name = self.findChild(QLineEdit, "signup_name_input").text()
        email = self.findChild(QLineEdit, "signup_email_input").text()
        password = self.findChild(QLineEdit, "signup_password_input").text()
        confirm_password = self.findChild(QLineEdit, "signup_confirm_password_input").text()
        terms_accepted = self.findChild(QCheckBox, "terms_check").isChecked()
        return name, email, password, confirm_password, terms_accepted

    def show_success_message(self, title, message):
        QMessageBox.information(self, title, message)
    
    def clear_inputs(self):
        # Clear all input fields
        self.findChild(QLineEdit, "email_input").clear()
        self.findChild(QLineEdit, "password_input").clear()

    def _create_left_side(self):
        """Create the left side branding and illustration"""
        left_widget = QFrame()
        left_widget.setStyleSheet(f"""
            background: qlineargradient(
                spread:pad, 
                x1:0, y1:0, 
                x2:1, y2:1, 
                stop:0 {ColorPalette.ACCENT_PRIMARY}, 
                stop:1 #6366F1
            );
        """)

        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(40, 40, 40, 40)

        # Logo
        logo = QLabel()
        logo_pixmap = QPixmap(100, 100)
        logo_pixmap.fill(Qt.transparent)

        painter = QPainter(logo_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw gradient circle
        gradient = QLinearGradient(0, 0, 100, 100)
        gradient.setColorAt(0, QColor(255, 255, 255, 80))
        gradient.setColorAt(1, QColor(255, 255, 255, 20))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(10, 10, 80, 80)

        # Draw "S" in the center
        painter.setPen(QPen(Qt.white))
        font = QFont()
        font.setBold(True)
        font.setPointSize(48)
        painter.setFont(font)
        painter.drawText(QRect(0, 0, 100, 100), Qt.AlignCenter, "S")

        painter.end()
        logo.setPixmap(logo_pixmap)
        logo.setAlignment(Qt.AlignCenter)

        # App name
        app_name = QLabel("StockMaster")
        app_name.setStyleSheet("""
            color: white;
            background: transparent;
            font-size: 28px;
            font-weight: bold;
            margin-top: 20px;
        """)
        app_name.setAlignment(Qt.AlignCenter)

        # Tagline
        tagline = QLabel("Invest Smarter, Not Harder")
        tagline.setStyleSheet("""
            background: transparent;
            color: rgba(255, 255, 255, 0.8);
            font-size: 16px;
        """)
        tagline.setAlignment(Qt.AlignCenter)

        # Add widgets to layout
        left_layout.addStretch(1)
        left_layout.addWidget(logo)
        left_layout.addWidget(app_name)
        left_layout.addWidget(tagline)
        left_layout.addStretch(2)

        return left_widget

    def _create_right_side(self):
        """Create the right side login/signup forms"""
        right_widget = QFrame()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(40, 40, 40, 40)
        right_layout.setSpacing(20)

        # Stacked widget to switch between login and signup
        self.stacked_widget = QStackedWidget()

        # Login Form
        login_form = self._create_login_form()

        # Signup Form
        signup_form = self._create_signup_form()

        # Add forms to stacked widget
        self.stacked_widget.addWidget(login_form)
        self.stacked_widget.addWidget(signup_form)

        # Add stacked widget to layout
        right_layout.addWidget(self.stacked_widget)

        return right_widget

    def _create_login_form(self):
        """Create the login form"""
        login_widget = QFrame()
        login_layout = QVBoxLayout(login_widget)
        login_layout.setSpacing(15)

        # Title
        title = QLabel("Welcome Back")
        title.setStyleSheet(f"""
            color: {ColorPalette.TEXT_PRIMARY};
            font-size: 24px;
            font-weight: bold;
        """)

        error_label = QLabel()
        error_label.setObjectName("error_message_label")
        error_label.setStyleSheet(f"""
                color: #FF5252;
                background-color: rgba(255, 82, 82, 0.1);
                border: 1px solid #FF5252;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
                margin: 10px 0px;
        """)
        error_label.setWordWrap(True)
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setVisible(False)  # Initially hidden

        # Subtitle
        subtitle = QLabel("Log in to continue")
        subtitle.setStyleSheet(f"""
            color: {ColorPalette.TEXT_SECONDARY};
            font-size: 14px;
        """)

        # Email input
        email_input = QLineEdit()
        email_input.setObjectName("email_input")
        email_input.setPlaceholderText("Email")
        email_input.setStyleSheet(GlobalStyle.INPUT_STYLE)

        # Password input
        password_input = QLineEdit()
        password_input.setObjectName("password_input")
        password_input.setPlaceholderText("Password")
        password_input.setEchoMode(QLineEdit.Password)
        password_input.setStyleSheet(GlobalStyle.INPUT_STYLE)

        # Remember me and forgot password
        remember_forgot_layout = QHBoxLayout()

        remember_check = QCheckBox("Remember me")
        remember_check.setStyleSheet(f"""
            color: {ColorPalette.TEXT_SECONDARY};
        """)

        forgot_password = QPushButton("Forgot Password?")
        forgot_password.setObjectName("forgot_password_btn")
        forgot_password.setStyleSheet(f"""
            color: {ColorPalette.ACCENT_PRIMARY};
            background: transparent;
            border: none;
            text-decoration: underline;
        """)

        remember_forgot_layout.addWidget(remember_check)
        remember_forgot_layout.addStretch(1)
        remember_forgot_layout.addWidget(forgot_password)

        # Login button
        login_btn = QPushButton("Log In")
        login_btn.setObjectName("login_btn")
        login_btn.setStyleSheet(GlobalStyle.PRIMARY_BUTTON)

        # Social login section
        social_login_layout = QHBoxLayout()

        # Google login
        google_btn = SocialLoginButton(
            "Icons/google", # Replace with actual Google icon path
            "Continue with Google",
            "#4285F4"
        )
        google_btn.setObjectName("google_login_btn")

        # Apple login
        apple_btn = SocialLoginButton(
            "Icons/apple", # Replace with actual Apple icon path
            "Continue with Apple",
            "#000000"
        )
        apple_btn.setObjectName("apple_login_btn")

        social_login_layout.addWidget(google_btn)
        social_login_layout.addWidget(apple_btn)

        # Signup prompt
        signup_prompt = QLabel("Don't have an account? ")
        signup_prompt.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY};")

        signup_link = QPushButton("Sign Up")
        signup_link.setStyleSheet(f"""
            color: {ColorPalette.ACCENT_PRIMARY};
            background: transparent;
            border: none;
            text-decoration: underline;
        """)

        signup_layout = QHBoxLayout()
        signup_layout.addWidget(signup_prompt)
        signup_layout.addWidget(signup_link)
        signup_layout.addStretch(1)

        # Add all to layout
        login_layout.addWidget(title)
        login_layout.addWidget(subtitle)
        login_layout.addSpacing(20)
        login_layout.addWidget(email_input)
        login_layout.addWidget(password_input)
        login_layout.addLayout(remember_forgot_layout)
        login_layout.addWidget(login_btn)
        login_layout.addSpacing(20)
        login_layout.addWidget(QLabel("Or continue with"))
        login_layout.addLayout(social_login_layout)
        login_layout.addLayout(signup_layout)
        login_layout.addStretch(1)

        # Connect signup link to switch to signup form
        signup_link.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        return login_widget

    def _create_signup_form(self):
        """Create the signup form"""
        signup_widget = QFrame()
        signup_layout = QVBoxLayout(signup_widget)
        signup_layout.setSpacing(15)

        # Title
        title = QLabel("Create Account")
        title.setStyleSheet(f"""
            color: {ColorPalette.TEXT_PRIMARY};
            font-size: 24px;
            font-weight: bold;
        """)

        # Subtitle
        subtitle = QLabel("Start your investment journey")
        subtitle.setStyleSheet(f"""
            color: {ColorPalette.TEXT_SECONDARY};
            font-size: 14px;
        """)

        # Full Name input
        name_input = QLineEdit()
        name_input.setObjectName("signup_name_input")
        name_input.setPlaceholderText("Full Name")
        name_input.setStyleSheet(GlobalStyle.INPUT_STYLE)

        # Email input
        email_input = QLineEdit()
        email_input.setObjectName("signup_email_input")
        email_input.setPlaceholderText("Email")
        email_input.setStyleSheet(GlobalStyle.INPUT_STYLE)

        # Password input
        password_input = QLineEdit()
        password_input.setObjectName("signup_password_input")
        password_input.setPlaceholderText("Password")
        password_input.setEchoMode(QLineEdit.Password)
        password_input.setStyleSheet(GlobalStyle.INPUT_STYLE)

        # Confirm Password input
        confirm_password_input = QLineEdit()
        confirm_password_input.setObjectName("signup_confirm_password_input")
        confirm_password_input.setPlaceholderText("Confirm Password")
        confirm_password_input.setEchoMode(QLineEdit.Password)
        confirm_password_input.setStyleSheet(GlobalStyle.INPUT_STYLE)

        # Terms and Conditions Checkbox
        terms_check = QCheckBox("I agree to the Terms and Conditions")
        terms_check.setObjectName("terms_check")
        terms_check.setStyleSheet(f"""
            color: {ColorPalette.TEXT_SECONDARY};
        """)

        # Signup button
        signup_btn = QPushButton("Sign Up")
        signup_btn.setObjectName("signup_btn")
        signup_btn.setStyleSheet(GlobalStyle.PRIMARY_BUTTON)

        # Social signup section
        social_signup_layout = QHBoxLayout()

        # Google signup
        google_btn = SocialLoginButton(
            "Icons/google", # Replace with actual Google icon path
            "Continue with Google",
            "#4285F4"
        )
        google_btn.setObjectName("google_signup_btn")

        # Apple signup
        apple_btn = SocialLoginButton(
            "Icons/apple", # Replace with actual Apple icon path
            "Continue with Apple",
            "#000000"
        )
        apple_btn.setObjectName("apple_login_btn")

        social_signup_layout.addWidget(google_btn)
        social_signup_layout.addWidget(apple_btn)

        # Login prompt
        login_prompt = QLabel("Already have an account? ")
        login_prompt.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY};")

        login_link = QPushButton("Log In")
        login_link.setStyleSheet(f"""
            color: {ColorPalette.ACCENT_PRIMARY};
            background: transparent;
            border: none;
            text-decoration: underline;
        """)

        login_layout = QHBoxLayout()
        login_layout.addWidget(login_prompt)
        login_layout.addWidget(login_link)
        login_layout.addStretch(1)

        # Add all to layout
        signup_layout.addWidget(title)
        signup_layout.addWidget(subtitle)
        signup_layout.addSpacing(20)
        signup_layout.addWidget(name_input)
        signup_layout.addWidget(email_input)
        signup_layout.addWidget(password_input)
        signup_layout.addWidget(confirm_password_input)
        signup_layout.addWidget(terms_check)
        signup_layout.addWidget(signup_btn)
        signup_layout.addSpacing(20)
        signup_layout.addWidget(QLabel("Or sign up with"))
        signup_layout.addLayout(social_signup_layout)
        signup_layout.addLayout(login_layout)
        signup_layout.addStretch(1)

        # Connect login link to switch to login form
        login_link.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))


        return signup_widget


class LoginInputEventFilter(QObject):
    """Event filter to handle input field focus events"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fields_with_errors = set()
    
    def eventFilter(self, obj, event):
        # Check if this is a focus in event on an input field with error
        if event.type() == QEvent.FocusIn and obj in self.fields_with_errors:
            # Reset the field style
            if hasattr(obj, 'original_style'):
                obj.setStyleSheet(obj.original_style)
                obj.setToolTip("")
                self.fields_with_errors.remove(obj)
                
        # Always return False to allow the event to be processed by Qt
        return False
    
    def add_field_with_error(self, field):
        """Add a field to the set of fields with errors"""
        self.fields_with_errors.add(field)

    def _modify_input_event_filter(self):
        """Update the input event filter to handle checkbox events"""
        original_event_filter = self.input_event_filter.eventFilter
        
        def new_event_filter(obj, event):
            # Handle text input fields as before
            if event.type() == QEvent.FocusIn and obj in self.input_event_filter.fields_with_errors:
                if hasattr(obj, 'original_style'):
                    obj.setStyleSheet(obj.original_style)
                    obj.setToolTip("")
                    self.input_event_filter.fields_with_errors.remove(obj)
            
            # Also handle checkbox state changes
            elif isinstance(obj, QCheckBox) and event.type() == QEvent.MouseButtonRelease:
                if obj in self.input_event_filter.fields_with_errors:
                    # Use QTimer to reset after click is processed
                    from PySide6.QtCore import QTimer
                    QTimer.singleShot(10, lambda: self._reset_checkbox_style(obj))
            
            # Always return False to allow normal event processing
            return False
        
        # Replace the event filter method
        self.input_event_filter.eventFilter = new_event_filter

    def _reset_checkbox_style(self, checkbox):
        """Reset checkbox style after state change"""
        if hasattr(checkbox, 'original_style'):
            checkbox.setStyleSheet(checkbox.original_style)
            checkbox.setToolTip("")
            self.input_event_filter.fields_with_errors.remove(checkbox)


class ForgotPasswordPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Title
        title = QLabel("Forgot Password")
        title.setStyleSheet(f"""
            color: {ColorPalette.TEXT_PRIMARY};
            font-size: 24px;
            font-weight: bold;
        """)

        # Subtitle
        subtitle = QLabel("Enter your email to reset your password")
        subtitle.setStyleSheet(f"""
            color: {ColorPalette.TEXT_SECONDARY};
            font-size: 14px;
        """)

        # Email input
        email_input = QLineEdit()
        email_input.setPlaceholderText("Email")
        email_input.setStyleSheet(GlobalStyle.INPUT_STYLE)

        # Reset password button
        reset_btn = QPushButton("Reset Password")
        reset_btn.setStyleSheet(GlobalStyle.PRIMARY_BUTTON)

        # Back to login link
        back_to_login = QPushButton("Back to Login")
        back_to_login.setStyleSheet(f"""
            color: {ColorPalette.ACCENT_PRIMARY};
            background: transparent;
            border: none;
            text-decoration: underline;
        """)

        # Add reset password functionality
        def handle_reset():
            email = email_input.text()
            success, message = AuthenticationManager.reset_password(email)

            if success:
                QMessageBox.information(self, "Password Reset", message)
            else:
                QMessageBox.warning(self, "Reset Error", message)

        reset_btn.clicked.connect(handle_reset)

        # Add back to login functionality
        def switch_to_login():
            if hasattr(self.parent(), 'stacked_widget'):
                self.parent().stacked_widget.setCurrentIndex(0)

        back_to_login.clicked.connect(switch_to_login)

        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        layout.addWidget(email_input)
        layout.addWidget(reset_btn)
        layout.addWidget(back_to_login)
        layout.addStretch(1)


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.setWindowTitle("StockMaster - Login")
        self.setMinimumSize(1000, 600)
        # Disable any resizing of the window
        self.setFixedSize(self.size())

        # Set dark theme background
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {ColorPalette.BG_DARK};
                color: {ColorPalette.TEXT_PRIMARY};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create stacked widget to manage different authentication pages
        self.stacked_widget = QStackedWidget()

        # Create pages
        login_page = LoginPage()
        forgot_password_page = ForgotPasswordPage()

        self.input_event_filter = LoginInputEventFilter(self)

        # Add pages to stacked widget
        self.stacked_widget.addWidget(login_page)
        self.stacked_widget.addWidget(forgot_password_page)

        # Add stacked widget to main layout
        main_layout.addWidget(self.stacked_widget)
        
        # Initialize loading overlay
        self.loading_overlay = None
    

    def init_loading_overlay(self):
        """Initialize the loading overlay"""
        # Import from the loading_overlay.py
        
        # Create loading overlay
        self.loading_overlay = LoadingOverlay(self)
        
        # Connect the finished signal to handle post-loading actions if needed
        self.loading_overlay.finished.connect(self.on_loading_finished)
    

    def on_loading_finished(self):
        """Handle actions after loading is complete"""
        # This method can be used to perform actions after loading completes
        pass

    def show_error_message(self, title, message):
        """Enhanced error message dialog"""
        # Create a custom styled message box
        error_box = QMessageBox(self)
        error_box.setWindowTitle(title)
        error_box.setText(message)
        error_box.setIcon(QMessageBox.Warning)
        
        # Style the message box
        error_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {ColorPalette.BG_DARK};
                color: {ColorPalette.TEXT_PRIMARY};
            }}
            QLabel {{
                color: {ColorPalette.TEXT_PRIMARY};
                font-size: 14px;
                min-width: 300px;
            }}
            QPushButton {{
                background-color: {ColorPalette.ACCENT_PRIMARY};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #5254c7;
            }}
        """)
        
        error_box.exec_()

    def show_success_message(self, title, message):
        """Show a success message dialog"""
        success_box = QMessageBox(self)
        success_box.setWindowTitle(title)
        success_box.setText(message)
        success_box.setIcon(QMessageBox.Information)
        
        # Style the message box
        success_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {ColorPalette.BG_DARK};
                color: {ColorPalette.TEXT_PRIMARY};
            }}
            QLabel {{
                color: {ColorPalette.TEXT_PRIMARY};
                font-size: 14px;
                min-width: 300px;
            }}
            QPushButton {{
                background-color: {ColorPalette.ACCENT_PRIMARY};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #5254c7;
            }}
        """)
        
        success_box.exec_()

    def show_input_error(self, error_type, message):
        # Show error message
        self.show_error_message("Login Error", message)
        
        # Get login page
        login_page = self.stacked_widget.widget(0)
        
        # Reset previous styles
        self._reset_all_input_styles(login_page)
        
        # Apply new error styles
        if error_type == "email" or error_type == "both":
            input_field = login_page.findChild(QLineEdit, "email_input")
            self._highlight_input_field(input_field, message)
            
        if error_type == "password" or error_type == "both":
            input_field = login_page.findChild(QLineEdit, "password_input")
            self._highlight_input_field(input_field, message)

    def _highlight_input_field(self, input_field, message):
        if not input_field:
            return
            
        # Store original style
        if not hasattr(input_field, 'original_style'):
            input_field.original_style = input_field.styleSheet()
        
        # Apply error styling
        input_field.setStyleSheet(f"""
            border: 2px solid #FF5252;
            background-color: rgba(255, 82, 82, 0.1);
            border-radius: 8px;
            padding: 10px;
        """)
        
        # Set tooltip
        input_field.setToolTip(message)
        
        # Install event filter
        input_field.installEventFilter(self.input_event_filter)
        self.input_event_filter.add_field_with_error(input_field)

    def _reset_input_style(self, page, field_id):
        """Reset an input field's style"""
        input_field = page.findChild(QLineEdit, field_id)
        if not input_field:
            return
            
        if hasattr(input_field, 'original_style'):
            input_field.setStyleSheet(input_field.original_style)
        
        input_field.setToolTip("")

    def _reset_all_input_styles(self, page):
        """Reset all input fields to original styles"""
        self._reset_input_style(page, "email_input")
        self._reset_input_style(page, "password_input")

    def navigate_to_home(self, user, user_stocks, user_transactions, firebaseUserId, balance, stocks_the_user_has, ai_advice):
        """Navigate to the home screen with the user's email"""
        from View.home_page import MainWindow
        
        # Create the home window (don't show yet)
        self.home_window = MainWindow(user, user_stocks, user_transactions, firebaseUserId, balance, stocks_the_user_has, ai_advice)
        
        # If loading overlay is active, update message
        if self.loading_overlay and self.loading_overlay.isVisible():
            self.loading_overlay.message_label.setText("Opening dashboard...")
            
            # Use a timer to show the home window after a brief delay
            QTimer.singleShot(800, self._complete_navigation)
        else:
            # If no loading overlay, just show the home window
            self._complete_navigation()
    
    def _complete_navigation(self):
        """Complete the navigation to the home screen"""
        if hasattr(self, 'home_window'):
            # Show the home window
            self.home_window.show()
            
            # Close the login window
            self.close()

    def show_signup_input_error(self, error_type, message):
        """
        Show error on signup input fields.
        Similar to show_input_error but for signup fields.
        """
        # Show error message
        self.show_error_message("Signup Error", message)
        
        # Get login page (which contains the signup form in the stacked widget)
        login_page = self.stacked_widget.widget(0)
        
        # Reset previous styles
        self._reset_all_signup_input_styles(login_page)
        
        # Apply new error styles based on error type
        if error_type == "name" or error_type == "all":
            input_field = login_page.findChild(QLineEdit, "signup_name_input")
            self._highlight_input_field(input_field, message)
            
        if error_type == "email" or error_type == "all" or error_type == "both":
            input_field = login_page.findChild(QLineEdit, "signup_email_input")
            self._highlight_input_field(input_field, message)
            
        if error_type == "password" or error_type == "all" or error_type == "both":
            input_field = login_page.findChild(QLineEdit, "signup_password_input")
            self._highlight_input_field(input_field, message)
            
        if error_type == "confirm_password" or error_type == "all":
            input_field = login_page.findChild(QLineEdit, "signup_confirm_password_input")
            self._highlight_input_field(input_field, message)
            
        if error_type == "terms_accepted" or error_type == "all":
            terms_field = login_page.findChild(QCheckBox, "terms_check")
            if terms_field:
                if not hasattr(terms_field, 'original_style'):
                    terms_field.original_style = terms_field.styleSheet()
                
                terms_field.setStyleSheet("""
                    QCheckBox {
                        color: #FF5252;
                    }
                    QCheckBox::indicator {
                        border: 2px solid #FF5252;
                        background-color: rgba(255, 82, 82, 0.1);
                    }
                """)
                terms_field.setToolTip(message)
                terms_field.installEventFilter(self.input_event_filter)
                self.input_event_filter.add_field_with_error(terms_field)

    def _reset_all_signup_input_styles(self, page):
        """Reset all signup input fields to original styles"""
        self._reset_input_style(page, "signup_name_input")
        self._reset_input_style(page, "signup_email_input")
        self._reset_input_style(page, "signup_password_input")
        self._reset_input_style(page, "signup_confirm_password_input")
        
        # Also reset terms checkbox
        terms_check = page.findChild(QCheckBox, "terms_check")
        if terms_check and hasattr(terms_check, 'original_style'):
            terms_check.setStyleSheet(terms_check.original_style)
            terms_check.setToolTip("")
            
    # Override resize event to make sure loading overlay always covers the window
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'loading_overlay') and self.loading_overlay:
            self.loading_overlay.resize(self.size())

class MainWindow(QWidget):
    def __init__(self, user_email=None):
        super().__init__()

        # Set up the window
        self.setWindowTitle("StockMaster Dashboard")
        self.setMinimumSize(1000, 700)



        # Use the dark theme from your existing color palette
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {ColorPalette.BG_DARK};
                color: {ColorPalette.TEXT_PRIMARY};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """)

        # Main layout
        layout = QVBoxLayout(self)

        # Welcome message
        welcome_label = QLabel(f"Welcome, {user_email or 'User'}!")
        welcome_label.setStyleSheet(f"""
            color: {ColorPalette.TEXT_PRIMARY};
            font-size: 24px;
            font-weight: bold;
        """)
        layout.addWidget(welcome_label)



class SpinnerWidget(QWidget):
    """Custom spinner widget that doesn't require external GIF files"""
    
    def __init__(self, parent=None, size=40, color=None):
        super().__init__(parent)
        
        self.setFixedSize(size, size)
        self.angle = 0
        self.color = color or QColor(ColorPalette.ACCENT_PRIMARY)
        
        # Create spin animation
        self.spin_animation = QPropertyAnimation(self, b"rotation_angle")
        self.spin_animation.setDuration(1000)  # 1 second per rotation
        self.spin_animation.setStartValue(0)
        self.spin_animation.setEndValue(360)
        self.spin_animation.setLoopCount(-1)  # Loop indefinitely
        self.spin_animation.setEasingCurve(QEasingCurve.Linear)
    
    def get_rotation_angle(self):
        return self.angle
    
    def set_rotation_angle(self, angle):
        self.angle = angle
        self.update()  # Trigger a repaint
    
    # Create a Qt property for the animation
    rotation_angle = Property(float, get_rotation_angle, set_rotation_angle)
    
    def start(self):
        """Start spinner animation"""
        self.spin_animation.start()
    
    def stop(self):
        """Stop spinner animation"""
        self.spin_animation.stop()
    
    def paintEvent(self, event):
        """Override paint event to draw spinner"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Save painter state
        painter.save()
        
        # Calculate center and radius
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) // 2 - 3
        
        # Set up pen for the arc
        painter.setPen(QPen(Qt.transparent))
        
        # Draw background circle (lighter)
        painter.setBrush(QBrush(QColor(100, 100, 100, 40)))
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        # Rotate painter for spinner effect
        painter.translate(center_x, center_y)
        painter.rotate(self.angle)
        painter.translate(-center_x, -center_y)
        
        # Draw spinner arc
        pen = QPen(self.color, 3, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)
        
        # Only draw a portion of the circle
        painter.drawArc(center_x - radius, center_y - radius, radius * 2, radius * 2, 0, 270 * 16)
        
        # Restore painter state
        painter.restore()

class AnimatedLoadingOverlay(LoadingOverlay):
    def __init__(self, parent=None, message="Please wait...", gif_path="Icons/spinner.gif"):
        # Initialize without the progress bar
        super().__init__(parent, message)
        
        # Remove the progress bar from layout
        self.layout().removeWidget(self.progress)
        self.progress.deleteLater()
        
        # Create animated spinner using QMovie
        self.spinner_label = QLabel()
        self.spinner_movie = QMovie(gif_path)
        
        # If GIF file doesn't exist, create a fallback spinner
        try:
            if not self.spinner_movie.isValid():
                raise FileNotFoundError("GIF file not found or invalid")
            
            self.spinner_movie.setScaledSize(QSize(64, 64))
            self.spinner_label.setMovie(self.spinner_movie)
            self.spinner_movie.start()
        except Exception as e:
            print(f"Error loading spinner GIF: {e}")
            # Create a fallback spinner (colored circle)
            spinner_pixmap = QPixmap(64, 64)
            spinner_pixmap.fill(Qt.transparent)
            
            painter = QPainter(spinner_pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QBrush(QColor(ColorPalette.ACCENT_PRIMARY)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(12, 12, 40, 40)
            painter.end()
            
            self.spinner_label.setPixmap(spinner_pixmap)
        
        # Add the spinner to the layout before the message
        self.layout().insertWidget(0, self.spinner_label, 0, Qt.AlignCenter)
    
    def start(self, message=None):
        """Start showing the animated loading overlay"""
        if hasattr(self, 'spinner_movie') and self.spinner_movie.isValid():
            self.spinner_movie.start()
        super().start(message)
    
    def stop(self):
        """Stop showing the animated loading overlay"""
        if hasattr(self, 'spinner_movie') and self.spinner_movie.isValid():
            self.spinner_movie.stop()
        super().stop()


    
if __name__ == "__main__":
    app = QApplication(sys.argv)


    # Set application-wide style
    app.setStyleSheet(f"""
        QWidget {{
            background-color: {ColorPalette.BG_DARK};
            color: {ColorPalette.TEXT_PRIMARY};
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
    """)

    # Show login window
    login_window = LoginWindow()
    login_window.show()

    sys.exit(app.exec())