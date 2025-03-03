# Step 1: Create a shared_components.py file

"""
shared_components.py - Common UI components and styles shared across the application
"""

# Colors, styles, and shared widgets
class ColorPalette:
    # Main backgrounds
    BG_DARK = "#121826"  # Main dark background - slightly bluer
    BG_CARD = "#1E293B"  # Card/panel background
    BG_SIDEBAR = "#0F172A"  # Sidebar darker background
    CARD_BG_DARKER = "#1A2234"  # Slightly darker card background for contrast

    # Accent colors
    ACCENT_PRIMARY = "#3B82F6"  # Primary blue
    ACCENT_SUCCESS = "#10B981"  # Success green
    ACCENT_WARNING = "#F59E0B"  # Warning orange
    ACCENT_DANGER = "#EF4444"  # Danger red
    ACCENT_INFO = "#6366F1"  # Info purple

    # Text colors
    TEXT_PRIMARY = "#F9FAFB"  # Primary text (white)
    TEXT_SECONDARY = "#9CA3AF"  # Secondary text (gray)
    TEXT_MUTED = "#6B7280"  # Muted text (darker gray)

    # Border colors
    BORDER_LIGHT = "#374151"  # Light border
    BORDER_DARK = "#1F2937"  # Dark border

    # Gradients
    GRADIENT_BLUE = ["#3B82F6", "#2563EB"]  # Blue gradient
    GRADIENT_GREEN = ["#10B981", "#059669"]  # Green gradient
    GRADIENT_PURPLE = ["#8B5CF6", "#7C3AED"]  # Purple gradient
    GRADIENT_ORANGE = ["#F59E0B", "#D97706"]  # Orange gradient
    GRADIENT_RED = ["#EF4444", "#DC2626"]  # Red gradient

    # Chart colors - more vibrant and distinct
    CHART_COLORS = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#6366F1",
                    "#8B5CF6", "#EC4899", "#14B8A6", "#F43F5E", "#84CC16"]

    @staticmethod
    def get_random_gradient():
        import random
        gradients = [
            ColorPalette.GRADIENT_BLUE,
            ColorPalette.GRADIENT_GREEN,
            ColorPalette.GRADIENT_PURPLE,
            ColorPalette.GRADIENT_ORANGE,
            ColorPalette.GRADIENT_RED
        ]
        return random.choice(gradients)

# Global Styling
class GlobalStyle:
    # Card style without border, just shadow and subtle background
    CARD_STYLE = f"""
        background-color: {ColorPalette.BG_CARD};
        border-radius: 12px;
        border: none;
    """

    # Text styles
    HEADER_STYLE = f"""
        color: {ColorPalette.TEXT_PRIMARY};
        font-size: 24px;
        font-weight: bold;
    """

    SUBHEADER_STYLE = f"""
        color: {ColorPalette.TEXT_PRIMARY};
        font-size: 18px;
        font-weight: bold;
    """

    BODY_STYLE = f"""
        color: {ColorPalette.TEXT_SECONDARY};
        font-size: 14px;
    """

    # Button styles - more rounded, no border
    PRIMARY_BUTTON = f"""
        QPushButton {{
            background-color: {ColorPalette.ACCENT_PRIMARY};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #2563EB;
        }}
        QPushButton:pressed {{
            background-color: #1D4ED8;
        }}
    """

    SECONDARY_BUTTON = f"""
        QPushButton {{
            background-color: rgba(255, 255, 255, 0.05);
            color: {ColorPalette.TEXT_PRIMARY};
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
        }}
        QPushButton:hover {{
            background-color: rgba(255, 255, 255, 0.1);
        }}
        QPushButton:pressed {{
            background-color: rgba(255, 255, 255, 0.05);
        }}
    """

    # Input styles - no border until focus
    INPUT_STYLE = f"""
        QLineEdit {{
            background-color: {ColorPalette.BG_DARK};
            color: {ColorPalette.TEXT_PRIMARY};
            border: none;
            border-radius: 8px;
            padding: 10px 15px;
        }}
        QLineEdit:focus {{
            background-color: rgba(59, 130, 246, 0.1);
            border: 1px solid {ColorPalette.ACCENT_PRIMARY};
        }}
    """

    # Table styles - cleaner with no border
    TABLE_STYLE = f"""
        QTableWidget {{
            background-color: transparent;
            color: {ColorPalette.TEXT_PRIMARY};
            border: none;
            gridline-color: transparent;
        }}
        QTableWidget::item {{
            padding: 12px;
            border-bottom: 1px solid {ColorPalette.BORDER_DARK};
        }}
        QTableWidget::item:selected {{
            background-color: rgba(59, 130, 246, 0.2);
            color: {ColorPalette.TEXT_PRIMARY};
        }}
        QHeaderView::section {{
            background-color: transparent;
            color: {ColorPalette.TEXT_SECONDARY};
            padding: 12px;
            border: none;
            font-weight: bold;
        }}
    """

    # Divider style - subtle
    DIVIDER_STYLE = f"""
        background-color: {ColorPalette.BORDER_DARK};
    """

# Copy the AvatarWidget class from your main.py
from PySide6.QtWidgets import QLabel, QSizePolicy
from PySide6.QtGui import QColor, QPixmap, QPainter, QBrush, QPen, QFont
from PySide6.QtCore import Qt, QRect

class AvatarWidget(QLabel):
    def __init__(self, name="Anonymous", size=40, background_color=None):
        super().__init__()
        self.name = name
        self.setFixedSize(size, size)
        self.background_color = background_color or ColorPalette.ACCENT_PRIMARY

        # Get initials from name
        self.initials = self.get_initials(name)

        # Create the avatar
        self.update_avatar()

        # Set rounded mask
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"border-radius: {size/2}px; color: white; font-weight: bold;")

    def get_initials(self, name):
        """Extract initials from a name"""
        parts = name.split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[1][0]}".upper()
        elif name:
            return name[0].upper()
        return "A"

    def update_avatar(self):
        """Update the avatar appearance"""
        size = self.width()
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw circle background
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(self.background_color)))
        painter.drawEllipse(0, 0, size, size)

        # Draw text
        painter.setPen(QPen(QColor("white")))
        font = QFont()
        font.setBold(True)
        font.setPointSize(size // 3)
        painter.setFont(font)
        painter.drawText(QRect(0, 0, size, size), Qt.AlignCenter, self.initials)

        painter.end()
        self.setPixmap(pixmap)