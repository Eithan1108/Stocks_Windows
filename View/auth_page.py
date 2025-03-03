import sys
import os
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QStackedWidget, QFrame,
                               QCheckBox, QMessageBox)
from PySide6.QtGui import (QColor, QFont, QPainter, QPixmap, QPen, QLinearGradient,
                           QBrush, QIcon)
from PySide6.QtCore import Qt, QSize, QRect, Signal
# In auth_page.py
from View.shared_components import ColorPalette, GlobalStyle, AvatarWidget

class SocialLoginButton(QPushButton):
    """Custom social login button with icon and styling"""
    def __init__(self, icon_path, text, color):
        super().__init__(text)

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
    def __init__(self, parent=None):
        super().__init__(parent)

        login_requested = Signal(str, str)  # email, password
        signup_requested = Signal(str, str, str, str, bool)  # name, email, password, confirm_password, terms_accepted
        forgot_password_requested = Signal(str)  # email

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

    # Add methods for the presenter to call
    def show_error_message(self, title, message):
        QMessageBox.warning(self, title, message)
    
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

        # Apple login
        apple_btn = SocialLoginButton(
            "Icons/apple", # Replace with actual Apple icon path
            "Continue with Apple",
            "#000000"
        )

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

        # Apple signup
        apple_btn = SocialLoginButton(
            "Icons/apple", # Replace with actual Apple icon path
            "Continue with Apple",
            "#000000"
        )

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

        # Add pages to stacked widget
        self.stacked_widget.addWidget(login_page)
        self.stacked_widget.addWidget(forgot_password_page)

        # Add stacked widget to main layout
        main_layout.addWidget(self.stacked_widget)
        connect_authentication_signals(login_page)  # Add this line

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

def connect_authentication_signals(login_page):
    # Login button
    login_btn = login_page.findChild(QPushButton, "login_btn")
    email_input = login_page.findChild(QLineEdit, "email_input")
    password_input = login_page.findChild(QLineEdit, "password_input")

    def handle_login():
        email = email_input.text()
        password = password_input.text()

        if AuthenticationManager.validate_login(email, password):
            # Import the home page here to avoid circular imports
            from View.home_page import MainWindow

            # Create the home window
            home_window = MainWindow(user_email=email)

            print("MainWindow created")

            # Ensure the window has a reference to prevent garbage collection
            login_page.home_window = home_window

            # Show the window
            home_window.show()

            print("MainWindow shown")

            # Close the login window
            login_page.window().close()

            # Keep the application running
            # Get the QApplication instance
            app = QApplication.instance()
            if app:
                # Process events to keep the window open
                app.exec()
        else:
            # Show error message
            QMessageBox.warning(login_page, "Login Error", "Invalid login credentials")

    login_btn.clicked.connect(handle_login)

# In View/auth_page.py
def navigate_to_home(self, email):
    """Navigate to the home screen with the user's email"""
    from View.home_page import MainWindow
    
    # Create and show the home window
    self.home_window = MainWindow(user_email=email)
    self.home_window.show()
    
    # Close the login window
    self.window().close()

    
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