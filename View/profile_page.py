import math
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QFrame, QHBoxLayout,
                               QLabel, QGridLayout, QScrollArea, QSizePolicy, QGraphicsDropShadowEffect,
                               QLineEdit, QTextEdit, QFormLayout, QStackedWidget, QComboBox, QFileDialog)
from PySide6.QtGui import (QColor, QPalette, QIcon, QPixmap, QPainter, QLinearGradient, QBrush, QPen,
                           QFont, QPainterPath, QCursor, QRadialGradient, QFontMetrics)
from PySide6.QtCore import (Qt, QSize, QRect, QTimer, QPointF, QEvent, QPoint, QEasingCurve,
                            QPropertyAnimation, Signal)

# Importing shared components from your existing codebase
# You'll need to adjust these imports based on your actual file structure
from View.shared_components import ColorPalette, GlobalStyle, AvatarWidget

class ProfileHeader(QFrame):
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

        title = QLabel("Profile")
        title.setStyleSheet(GlobalStyle.HEADER_STYLE)

        subtitle = QLabel("Manage your personal information")
        subtitle.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 14px;")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        # Add title layout to main layout
        layout.addLayout(title_layout)
        layout.addStretch(1)

        # Add edit profile button
        edit_btn = QPushButton("Edit Profile")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setStyleSheet(GlobalStyle.PRIMARY_BUTTON)
        edit_btn.setFixedHeight(40)
        edit_btn.setMinimumWidth(120)
        layout.addWidget(edit_btn)

class ProfileCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Setup styling
        self.setStyleSheet(GlobalStyle.CARD_STYLE)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))  # More subtle shadow
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # Setup content
        self._setup_ui()

    def _setup_ui(self):
        # Profile info layout with avatar and details side by side
        profile_layout = QHBoxLayout()
        profile_layout.setSpacing(25)
        
        # Avatar - large size for profile page
        self.avatar = AvatarWidget("John Doe", size=120)
        self.avatar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        # Change profile photo button
        change_photo_btn = QPushButton("Change Photo")
        change_photo_btn.setCursor(Qt.PointingHandCursor)
        change_photo_btn.setStyleSheet(GlobalStyle.SECONDARY_BUTTON)
        change_photo_btn.setFixedWidth(120)
        
        # Avatar column with button
        avatar_column = QVBoxLayout()
        avatar_column.setAlignment(Qt.AlignCenter)
        avatar_column.addWidget(self.avatar)
        avatar_column.addSpacing(10)
        avatar_column.addWidget(change_photo_btn)
        avatar_column.addStretch()
        
        # Profile details in a form layout
        details_layout = QFormLayout()
        details_layout.setSpacing(15)
        details_layout.setContentsMargins(0, 10, 0, 10)
        
        # Create styled labels
        name_title = QLabel("Full Name")
        name_title.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
        name_value = QLabel("John Doe")
        name_value.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-size: 15px; font-weight: bold;")
        
        email_title = QLabel("Email")
        email_title.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
        email_value = QLabel("john.doe@example.com")
        email_value.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-size: 15px; font-weight: bold;")
        
        phone_title = QLabel("Phone")
        phone_title.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
        phone_value = QLabel("+1 (555) 123-4567")
        phone_value.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-size: 15px; font-weight: bold;")
        
        location_title = QLabel("Location")
        location_title.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
        location_value = QLabel("New York, USA")
        location_value.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-size: 15px; font-weight: bold;")
        
        joined_title = QLabel("Member Since")
        joined_title.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
        joined_value = QLabel("March 2022")
        joined_value.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-size: 15px; font-weight: bold;")
        
        # Add to form layout
        details_layout.addRow(name_title, name_value)
        details_layout.addRow(email_title, email_value)
        details_layout.addRow(phone_title, phone_value)
        details_layout.addRow(location_title, location_value)
        details_layout.addRow(joined_title, joined_value)
        
        # Add avatar and details to profile layout
        profile_layout.addLayout(avatar_column)
        profile_layout.addLayout(details_layout)
        profile_layout.addStretch(1)
        
        # Add profile layout to main layout
        self.layout.addLayout(profile_layout)

class PreferencesCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Setup styling
        self.setStyleSheet(GlobalStyle.CARD_STYLE)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # Title
        title_label = QLabel("Preferences")
        title_label.setStyleSheet(GlobalStyle.SUBHEADER_STYLE)
        self.layout.addWidget(title_label)
        
        # Setup content
        self._setup_ui()

    def _setup_ui(self):
        # Grid layout for preferences
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        
        # Language preference
        language_layout = QVBoxLayout()
        language_title = QLabel("Language")
        language_title.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold; font-size: 14px;")
        
        language_combo = QComboBox()
        language_combo.addItems(["English", "Spanish", "French", "German", "Chinese"])
        language_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {ColorPalette.BG_DARK};
                color: {ColorPalette.TEXT_PRIMARY};
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                min-height: 38px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border: none;
            }}
        """)
        
        language_layout.addWidget(language_title)
        language_layout.addWidget(language_combo)
        
        # Theme preference
        theme_layout = QVBoxLayout()
        theme_title = QLabel("Theme")
        theme_title.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold; font-size: 14px;")
        
        theme_combo = QComboBox()
        theme_combo.addItems(["Dark Theme", "Light Theme", "System Default"])
        theme_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {ColorPalette.BG_DARK};
                color: {ColorPalette.TEXT_PRIMARY};
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                min-height: 38px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border: none;
            }}
        """)
        
        theme_layout.addWidget(theme_title)
        theme_layout.addWidget(theme_combo)
        
        # Notification settings
        notif_layout = QVBoxLayout()
        notif_title = QLabel("Notifications")
        notif_title.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold; font-size: 14px;")
        
        notif_combo = QComboBox()
        notif_combo.addItems(["All Notifications", "Important Only", "None"])
        notif_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {ColorPalette.BG_DARK};
                color: {ColorPalette.TEXT_PRIMARY};
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                min-height: 38px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border: none;
            }}
        """)
        
        notif_layout.addWidget(notif_title)
        notif_layout.addWidget(notif_combo)
        
        # Date format
        date_layout = QVBoxLayout()
        date_title = QLabel("Date Format")
        date_title.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold; font-size: 14px;")
        
        date_combo = QComboBox()
        date_combo.addItems(["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD"])
        date_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {ColorPalette.BG_DARK};
                color: {ColorPalette.TEXT_PRIMARY};
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                min-height: 38px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border: none;
            }}
        """)
        
        date_layout.addWidget(date_title)
        date_layout.addWidget(date_combo)
        
        # Add layouts to grid
        grid_layout.addLayout(language_layout, 0, 0)
        grid_layout.addLayout(theme_layout, 0, 1)
        grid_layout.addLayout(notif_layout, 1, 0)
        grid_layout.addLayout(date_layout, 1, 1)
        
        # Add grid to main layout
        self.layout.addLayout(grid_layout)
        
        # Add spacer
        self.layout.addStretch(1)
        
        # Save preferences button
        save_btn = QPushButton("Save Preferences")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(GlobalStyle.PRIMARY_BUTTON)
        save_btn.setFixedHeight(40)
        self.layout.addWidget(save_btn)

class SecurityCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Setup styling
        self.setStyleSheet(GlobalStyle.CARD_STYLE)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # Title
        title_label = QLabel("Security Settings")
        title_label.setStyleSheet(GlobalStyle.SUBHEADER_STYLE)
        self.layout.addWidget(title_label)
        
        # Setup content
        self._setup_ui()

    def _setup_ui(self):
        # Last login info
        login_layout = QHBoxLayout()
        login_icon = QLabel("🔒")
        login_icon.setFixedSize(24, 24)
        login_icon.setAlignment(Qt.AlignCenter)
        login_info = QLabel("Last login: Today, 10:35 AM • New York, USA")
        login_info.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 13px;")
        
        login_layout.addWidget(login_icon)
        login_layout.addWidget(login_info)
        login_layout.addStretch()
        
        self.layout.addLayout(login_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"background-color: {ColorPalette.BORDER_DARK};")
        separator.setFixedHeight(1)
        
        self.layout.addWidget(separator)
        
        # Security options
        # Password change
        change_password_btn = QPushButton("Change Password")
        change_password_btn.setCursor(Qt.PointingHandCursor)
        change_password_btn.setStyleSheet(GlobalStyle.SECONDARY_BUTTON)
        change_password_btn.setFixedHeight(40)
        
        # 2FA setup
        twofa_btn = QPushButton("Set Up Two-Factor Authentication")
        twofa_btn.setCursor(Qt.PointingHandCursor)
        twofa_btn.setStyleSheet(GlobalStyle.SECONDARY_BUTTON)
        twofa_btn.setFixedHeight(40)
        
        # Device management
        devices_btn = QPushButton("Manage Connected Devices")
        devices_btn.setCursor(Qt.PointingHandCursor)
        devices_btn.setStyleSheet(GlobalStyle.SECONDARY_BUTTON)
        devices_btn.setFixedHeight(40)
        
        # Add buttons to layout with spacing
        self.layout.addWidget(change_password_btn)
        self.layout.addWidget(twofa_btn)
        self.layout.addWidget(devices_btn)
        
        self.layout.addStretch(1)

class ProfilePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet(f"background-color: {ColorPalette.BG_DARK};")
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        self.header = ProfileHeader()
        layout.addWidget(self.header)
        
        # Scrollable content area for responsiveness
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """)
        
        # Container for all content
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(20)
        
        # Profile info card
        self.profile_card = ProfileCard()
        self.content_layout.addWidget(self.profile_card)
        
        # Preferences card
        self.preferences_card = PreferencesCard()
        self.content_layout.addWidget(self.preferences_card)
        
        # Security card
        self.security_card = SecurityCard()
        self.content_layout.addWidget(self.security_card)
        
        # Set the scroll area widget and add to main layout
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)
        
        # Install event filter to handle resize events
        self.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Handle resize events to adjust layout responsively"""
        if obj == self and event.type() == QEvent.Resize:
            width = self.width()
            
            # For smaller screens, adjust margins
            if width < 800:
                self.content_layout.setContentsMargins(0, 0, 0, 0)
            else:
                self.content_layout.setContentsMargins(0, 0, 0, 0)
                
        return super().eventFilter(obj, event)

# For testing
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = ProfilePage()
    window.setWindowTitle("User Profile")
    window.resize(900, 650)
    window.show()
    sys.exit(app.exec())