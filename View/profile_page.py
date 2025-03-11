import math
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QFrame, QHBoxLayout,
                               QLabel, QSizePolicy, QGraphicsDropShadowEffect, QLineEdit, QFormLayout,
                               QScrollArea)
from PySide6.QtGui import QColor, QFont, QPainter, QBrush, QPen
from PySide6.QtCore import Qt, QEvent, QSize, QTimer

# Importing existing color palette and styles
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QFrame, QHBoxLayout,
                               QLabel, QSizePolicy, QGraphicsDropShadowEffect, QLineEdit, QFormLayout)
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt

# Define color palette and style constants for dark theme
class ColorPalette:
    BG_DARK = "#151825"         # Dark blue background
    BG_CARD = "#1E2235"         # Slightly lighter blue for cards
    PRIMARY = "#3D7FEE"         # Bright blue for primary elements
    PRIMARY_DARK = "#3270DE"    # Slightly darker blue for hover states
    TEXT_PRIMARY = "#FFFFFF"    # White text
    TEXT_SECONDARY = "#9A9CB0"  # Muted blue-gray for secondary text
    BORDER_DARK = "#252A3D"     # Dark border color

class GlobalStyle:
    CARD_STYLE = f"""
        background-color: {ColorPalette.BG_CARD};
        border-radius: 8px;
        border: 1px solid {ColorPalette.BORDER_DARK};
    """
    HEADER_STYLE = f"""
        color: {ColorPalette.TEXT_PRIMARY};
        font-size: 24px;
        font-weight: bold;
    """
    SUBHEADER_STYLE = f"""
        color: {ColorPalette.TEXT_PRIMARY};
        font-size: 18px;
        font-weight: bold;
        border: none;
    """
    PRIMARY_BUTTON = f"""
        QPushButton {{
            background-color: {ColorPalette.PRIMARY};
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {ColorPalette.PRIMARY_DARK};
        }}
    """
    SECONDARY_BUTTON = f"""
        QPushButton {{
            background-color: {ColorPalette.BG_CARD};
            color: {ColorPalette.TEXT_PRIMARY};
            border: 1px solid {ColorPalette.BORDER_DARK};
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background-color: #252A3D;
        }}
    """
    INPUT_STYLE = f"""
        QLineEdit {{
            background-color: {ColorPalette.BG_DARK};
            color: {ColorPalette.TEXT_PRIMARY};
            border: 1px solid {ColorPalette.BORDER_DARK};
            border-radius: 4px;
            padding: 8px;
            font-size: 14px;
        }}
    """

class AccountHeader(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(80)
        self.setStyleSheet("""
            background-color: transparent;
            border: none;
        """)

        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Page title
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)

        title = QLabel("Account")
        title.setStyleSheet(GlobalStyle.HEADER_STYLE)

        subtitle = QLabel("Manage your account balance")
        subtitle.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 14px; border: none;")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        # Add title layout to main layout
        layout.addLayout(title_layout)
        layout.addStretch(1)

        # Add edit account button
        edit_btn = QPushButton("Account Settings")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setStyleSheet(GlobalStyle.PRIMARY_BUTTON)
        edit_btn.setFixedHeight(40)
        edit_btn.setMinimumWidth(120)
        layout.addWidget(edit_btn)

class AccountInfoCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Setup styling
        self.setStyleSheet(GlobalStyle.CARD_STYLE)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(150)

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Account Information")
        title.setStyleSheet(GlobalStyle.SUBHEADER_STYLE)
        layout.addWidget(title)
        
        # Account details
        info_layout = QFormLayout()
        info_layout.setSpacing(10)
        info_layout.setHorizontalSpacing(40)
        
        # Create labels with proper styling
        account_name_label = QLabel("User Name:")
        account_name_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 14px; border: none;")
        self.account_name = QLabel("Loading...")
        self.account_name.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-size: 15px; font-weight: bold; border: none;")
        
        account_id_label = QLabel("Email:")
        account_id_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 14px; border: none;")
        self.account_id = QLabel("Loading...")
        self.account_id.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-size: 15px; font-weight: bold; border: none;")
        
        account_type_label = QLabel("Account Type:")
        account_type_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 14px; border: none;")
        self.account_type = QLabel("Loading...")
        self.account_type.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-size: 15px; font-weight: bold; border: none;")
        
        # Add to form layout
        info_layout.addRow(account_name_label, self.account_name)
        info_layout.addRow(account_id_label, self.account_id)
        info_layout.addRow(account_type_label, self.account_type)
        
        layout.addLayout(info_layout)

    def update_info(self, name, id, account_type):
        """Update account information"""
        self.account_name.setText(name)
        self.account_id.setText(id)
        self.account_type.setText(account_type)

class AccountBalanceCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Setup styling
        self.setStyleSheet(GlobalStyle.CARD_STYLE)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(120)

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(5)
        
        # Account Balance Label
        balance_label = QLabel("Account Balance")
        balance_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 14px; border: none;")
        layout.addWidget(balance_label)
        
        # Balance Amount
        self.balance_amount = QLabel("Loading...")
        self.balance_amount.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-size: 28px; font-weight: bold; border: none;")
        layout.addWidget(self.balance_amount)
        
        # Last updated
        self.last_updated = QLabel("Last updated: --")
        self.last_updated.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px; border: none;")
        layout.addWidget(self.last_updated)
        
    def update_balance(self, balance, update_time=None):
        """Update balance information"""
        self.balance_amount.setText(balance)
        
        if update_time:
            self.last_updated.setText(f"Last updated: {update_time}")
        else:
            # Get current time
            from datetime import datetime
            current_time = datetime.now().strftime("%B %d, %Y %I:%M %p")
            self.last_updated.setText(f"Last updated: {current_time}")

class AddMoneyCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Setup styling
        self.setStyleSheet(GlobalStyle.CARD_STYLE)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(200)

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Add Money to Account")
        title.setStyleSheet(GlobalStyle.SUBHEADER_STYLE)
        layout.addWidget(title)
        
        # Form layout for amount input
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        amount_label = QLabel("Amount ($)")
        amount_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 14px;")
        
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount")
        self.amount_input.setStyleSheet(GlobalStyle.INPUT_STYLE)
        self.amount_input.setFixedHeight(40)
        
        form_layout.addRow(amount_label, self.amount_input)
        layout.addLayout(form_layout)
        

        # Add money button
        add_money_btn = QPushButton("Add Money")
        add_money_btn.setCursor(Qt.PointingHandCursor)
        add_money_btn.setStyleSheet(GlobalStyle.PRIMARY_BUTTON)
        add_money_btn.setFixedHeight(40)
        layout.addWidget(add_money_btn)

        self.add_money_btn = add_money_btn

    def get_add_money_button(self):
        """
        Return the add money button
        """
        return self.add_money_btn
    
    def get_money_amount(self):
        """
        Get the amount entered by the user
        """
        return self.amount_input.text()

class ProfilePage(QWidget):
    def __init__(self, user=None, balance=None, firebaseId=None, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet(f"background-color: {ColorPalette.BG_DARK};")
        self.setMinimumSize(600, 730)  # Set minimum window size
        # Set resizing disabled
        self.setFixedSize(self.size())

        self.user = user
        self.balance = balance
        self.firebaseId = firebaseId
        print("User from profile page:", self.user)
        print("Balance from profile page:", self.balance)
        print("Firebase ID from profile page:", self.firebaseId)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        self.header = AccountHeader()
        layout.addWidget(self.header)
        
        # Scrollable content area for responsiveness
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollArea > QWidget > QWidget {{
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: {ColorPalette.BG_DARK};
                width: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {ColorPalette.BORDER_DARK};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        # Container for all content
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(20)
        
        # Account info card
        self.account_info = AccountInfoCard()
        self.content_layout.addWidget(self.account_info)
        
        # Balance card
        self.balance_card = AccountBalanceCard()
        self.content_layout.addWidget(self.balance_card)
        
        # Add money card
        self.add_money_card = AddMoneyCard()
        self.content_layout.addWidget(self.add_money_card)
        
        # Status message (for success/error messages)
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: white; font-weight: bold; padding: 8px;")
        self.status_label.setVisible(False)  # Initially hidden
        self.content_layout.addWidget(self.status_label)
        
        # Set the scroll area widget and add to main layout
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)
        
        # Add stretch to push everything to the top
        self.content_layout.addStretch(1)

    def set_presenter(self, presenter):
        """
        Set the presenter for this view
        """
        self.presenter = presenter

    def get_add_money_button(self):
        """
        Return the add money button
        """
        return self.add_money_card.get_add_money_button()
    
    def get_money_amount(self):
        """
        Get the amount entered by the user
        """
        return self.add_money_card.get_money_amount()
    
    def clear_money_input(self):
        """
        Clear the money input field
        """
        self.add_money_card.amount_input.clear()
    
    def update_user_info(self, user_data):
        """
        Update the user information displayed in the account info card
        """
        if not user_data:
            return
        
        # Get name from user_data
        display_name = user_data.get('username', 'N/A')
        user_id = user_data.get('email', 'N/A')
        account_type = user_data.get('accountType', 'Standard')
        
        # Update the account info card
        self.account_info.update_info(display_name, user_id, account_type)
        
        # Update the class variable
        self.user = user_data
    
    def update_balance(self, balance):
        """
        Update the balance displayed in the balance card
        """
        if balance is None:
            return
            
        # Format the balance with commas and 2 decimal places
        formatted_balance = "${:,.2f}".format(float(balance))
        
        # Update the balance card
        from datetime import datetime
        current_time = datetime.now().strftime("%B %d, %Y %I:%M %p")
        self.balance_card.update_balance(formatted_balance, current_time)
        
        # Update the class variable
        self.balance = balance
    
    def show_error_message(self, message):
        """
        Display an error message to the user
        """
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"""
            color: #FF5252;
            background-color: rgba(255, 82, 82, 0.1);
            border: 1px solid #FF5252;
            border-radius: 4px;
            padding: 8px;
            font-weight: bold;
        """)
        self.status_label.setVisible(True)
        
        # Hide the message after 5 seconds
        from PySide6.QtCore import QTimer
        QTimer.singleShot(5000, lambda: self.status_label.setVisible(False))
    
    def show_success_message(self, message):
        """
        Display a success message to the user
        """
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"""
            color: #4CAF50;
            background-color: rgba(76, 175, 80, 0.1);
            border: 1px solid #4CAF50;
            border-radius: 4px;
            padding: 8px;
            font-weight: bold;
        """)
        self.status_label.setVisible(True)
        
        # Hide the message after 5 seconds
        from PySide6.QtCore import QTimer
        QTimer.singleShot(5000, lambda: self.status_label.setVisible(False))

# For testing
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = ProfilePage()
    window.setWindowTitle("Account Information")
    window.resize(600, 650)
    window.show()
    sys.exit(app.exec())