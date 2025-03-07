import math
import sys
import os
import random
from datetime import datetime, timedelta

from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QFrame, QHBoxLayout,
                               QLabel, QGridLayout, QScrollArea, QSizePolicy, QGraphicsDropShadowEffect,
                               QLayout, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QMenu,
                               QComboBox, QProgressBar, QToolButton, QTabWidget, QSpacerItem, QBoxLayout)
from PySide6.QtGui import (QColor, QPalette, QIcon, QPixmap, QPainter, QLinearGradient, QBrush, QPen,
                           QFont, QPainterPath, QCursor, QRadialGradient, QFontMetrics, QFontDatabase)
from PySide6.QtCore import (Qt, QSize, QRect, QTimer, QPointF, QEvent, QPoint, QEasingCurve,
                            QPropertyAnimation, Signal, QUrl, QMargins)
from PySide6.QtSvg import QSvgRenderer
from View.ai_advisor_window import AIAdvisorWindow
from View.shared_components import ColorPalette, GlobalStyle, AvatarWidget
from View.protofilio_view import PortfolioPage
from View.transaction_view import TransactionsPage
from View.profile_page import ProfilePage

# Modern color palette
# Modern color palette with improved contrast and subtle variations



def load_fonts():
    """Load custom fonts for the application"""
    # In a real app, you would include these font files with your application
    # For this example, we'll use system fonts with fallbacks
    pass

# Icon button for sidebar
class SidebarButton(QPushButton):
    def __init__(self, icon_name, text="", parent=None, is_active=False):
        super().__init__(parent)
        self.setText(text)
        self.is_active = is_active
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(50)

        # Set icon if provided and exists
        if icon_name and os.path.exists(icon_name):
            self.setIcon(QIcon(icon_name))
            self.setIconSize(QSize(20, 20))
        else:
            # Create a placeholder icon
            self.create_placeholder_icon(icon_name[0] if icon_name else "X")

        self.update_styles()

    def create_placeholder_icon(self, text):
        """Create a placeholder icon with text"""
        size = 20
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw background
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(ColorPalette.ACCENT_PRIMARY))
        painter.drawRoundedRect(0, 0, size, size, 4, 4)

        # Draw text
        painter.setPen(Qt.white)
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        painter.setFont(font)
        painter.drawText(QRect(0, 0, size, size), Qt.AlignCenter, text)

        painter.end()
        self.setIcon(QIcon(pixmap))
        self.setIconSize(QSize(20, 20))

    def update_styles(self):
        """Update button styles based on active state"""
        if self.is_active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {ColorPalette.ACCENT_PRIMARY};
                    color: {ColorPalette.TEXT_PRIMARY};
                    border: none;
                    border-radius: 8px;
                    text-align: left;
                    padding: 10px 15px;
                }}
                QPushButton:hover {{
                    background-color: {ColorPalette.ACCENT_PRIMARY};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {ColorPalette.TEXT_SECONDARY};
                    border: none;
                    border-radius: 8px;
                    text-align: left;
                    padding: 10px 15px;
                }}
                QPushButton:hover {{
                    background-color: rgba(255, 255, 255, 0.1);
                    color: {ColorPalette.TEXT_PRIMARY};
                }}
            """)

    def setActive(self, active):
        """Set the active state of the button"""
        self.is_active = active
        self.update_styles()

    def mousePressEvent(self, event):
        """Handle mouse press event"""
        super().mousePressEvent(event)
        # Could emit a custom signal here to handle navigation

class Card(QFrame):
    def __init__(self, title="", content="", parent=None, min_height=150):
        super().__init__(parent)
        self.title = title
        self.content = content

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

        # Title
        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet(GlobalStyle.SUBHEADER_STYLE)
            self.layout.addWidget(title_label)

        # Content
        if content:
            content_label = QLabel(content)
            content_label.setStyleSheet(GlobalStyle.BODY_STYLE)
            content_label.setWordWrap(True)
            self.layout.addWidget(content_label)

        # Set minimum height
        self.setMinimumHeight(min_height)

# Improved portfolio summary card with better space utilization
class PortfolioSummaryCard(Card):
    def __init__(self, title="Portfolio Value", balance="$1,234,567.89", change="+4.5%", parent=None):
        super().__init__(title="", parent=parent)
        self.balance = balance
        self.change = change
        self.trend_data = self._generate_trend_data()

        # Get gradient colors for orange theme
        self.color_start = "#F59E0B"  # Orange start
        self.color_end = "#D97706"    # Darker orange end

        # Update the style with gradient background
        self.setStyleSheet(f"""
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                stop:0 {self.color_start}, stop:1 {self.color_end});
            border-radius: 12px;
            border: none;
        """)

        # Set content
        self._setup_ui()

        # Connect resize event handlers
        self.installEventFilter(self)

    def _setup_ui(self):
        """Setup the card UI with better space utilization"""
        # Main layout to organize content
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Top section with value and change
        top_section = QHBoxLayout()
        top_section.setSpacing(15)

        # Value/Change section (left)
        value_section = QVBoxLayout()
        value_section.setSpacing(5)

        # Balance value - large and prominent
        balance_label = QLabel(self.balance)
        balance_label.setStyleSheet("""
            color: white;
            font-size: 36px;
            font-weight: bold;
            background: transparent;
        """)

        # Change percentage with background
        change_str = self.change
        if not change_str.startswith("+") and not change_str.startswith("-"):
            if float(change_str.rstrip("%")) > 0:
                change_str = f"+{change_str}"

        is_positive = not change_str.startswith("-")

        change_label = QLabel(change_str)
        change_label.setStyleSheet(f"""
            color: white;
            font-size: 16px;
            font-weight: bold;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
            padding: 4px 10px;
        """)

        value_section.addWidget(balance_label)
        value_section.addWidget(change_label)
        value_section.setAlignment(change_label, Qt.AlignLeft)

        # Add value section to top section
        top_section.addLayout(value_section)

        # Add spacer to push time filters to the right
        top_section.addStretch(1)

        # Add top section to main layout
        main_layout.addLayout(top_section)

        # Graph takes the remaining space
        self.graph_label = QLabel()
        self.graph_label.setMinimumHeight(150)
        self.graph_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.graph_label.setStyleSheet("background: transparent;")
        main_layout.addWidget(self.graph_label, 1)  # 1 = stretch factor

        # Set the layout
        self.layout.addLayout(main_layout)

        # Initial graph update
        self._update_graph()

    def _generate_trend_data(self):
        """Generate sample trend data for the chart"""
        import random
        points = []
        num_points = 40  # More points for a smoother curve

        # Generate a more realistic looking stock chart
        base = 100
        for i in range(num_points):
            # Add some randomness with an overall upward trend
            change = random.uniform(-3, 5)
            if i > 0:
                base = max(base + change, 50)  # Ensure value doesn't go too low
            points.append(base)

        return points

    def eventFilter(self, obj, event):
        """Handle resize events"""
        if obj == self and event.type() == QEvent.Resize:
            self._update_graph()
        return super().eventFilter(obj, event)

    def _update_graph(self):
        """Update the chart visualization with recursive protection"""
        # Prevent recursive calls
        if hasattr(self, '_is_updating_graph') and self._is_updating_graph:
            return

        self._is_updating_graph = True

        try:
            width = self.graph_label.width()
            height = self.graph_label.height()

            if width <= 0 or height <= 0:
                return

            pixmap = QPixmap(width, height)
            pixmap.fill(Qt.transparent)

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)

            # Determine min and max values for scaling
            min_val = min(self.trend_data)
            max_val = max(self.trend_data)
            value_range = max(0.1, max_val - min_val)  # Avoid division by zero

            # Create points for the chart
            points = []
            num_points = len(self.trend_data)

            # Adjust number of points based on width to avoid overcrowding
            step = max(1, int(num_points / (width / 4)))
            visible_points = [self.trend_data[i] for i in range(0, num_points, step)]

            # Add the last point to ensure the graph goes all the way
            if (num_points - 1) % step != 0:
                visible_points.append(self.trend_data[-1])

            # Create point coordinates
            if len(visible_points) > 0:  # Check if we have points
                for i, val in enumerate(visible_points):
                    x = i * (width / (len(visible_points) - 1)) if len(visible_points) > 1 else width/2
                    y = height - ((val - min_val) / value_range * height * 0.8) - (height * 0.1)
                    points.append(QPointF(x, y))

                if points:  # Check if we have valid points
                    # Create line path
                    path = QPainterPath()
                    path.moveTo(points[0])
                    for point in points[1:]:
                        path.lineTo(point)

                    # Create fill path
                    fill_path = QPainterPath(path)
                    fill_path.lineTo(width, height)
                    fill_path.lineTo(0, height)
                    fill_path.closeSubpath()

                    # Draw fill with gradient
                    gradient = QLinearGradient(0, 0, 0, height)
                    gradient.setColorAt(0, QColor(255, 255, 255, 80))
                    gradient.setColorAt(1, QColor(255, 255, 255, 0))
                    painter.fillPath(fill_path, gradient)

                    # Draw the line
                    pen = QPen(QColor(255, 255, 255, 230))
                    pen.setWidth(2)
                    painter.setPen(pen)
                    painter.drawPath(path)

                    # Draw points at data locations - only if we have enough space
                    if width > 300 and len(points) < 20:
                        painter.setPen(Qt.NoPen)
                        painter.setBrush(QBrush(QColor(255, 255, 255)))
                        for point in points:
                            painter.drawEllipse(point, 2, 2)

                    # Draw a larger highlight point at the last data point
                    if points:
                        painter.drawEllipse(points[-1], 4, 4)

            painter.end()
            self.graph_label.setPixmap(pixmap)
        finally:
            self._is_updating_graph = False


# Improved stock item with responsive design
class StockItem(QFrame):
    def __init__(self, stock_data, is_last=False):
        super().__init__()
        self.stock_data = stock_data
        self.is_last = is_last

        # Style with only bottom border when needed
        border_style = "none" if is_last else f"1px solid {ColorPalette.BORDER_DARK}"
        self.setStyleSheet(f"""
            background-color: transparent;
            border: none;
            border-bottom: {border_style};
        """)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(65)  # Slightly reduced height

        # Main layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 8, 10, 8)  # Reduced margins
        self.layout.setSpacing(12)

        # Create and add components
        self._setup_ui()

        # For responsive design
        self.installEventFilter(self)

    def _setup_ui(self):
        # Icon with company initials
        initials = self._get_stock_initials(self.stock_data["name"])
        color = self._get_stock_color(self.stock_data["name"])
        self.icon = AvatarWidget(initials, size=38, background_color=color)  # Slightly smaller
        self.layout.addWidget(self.icon)

        # Stock info (name and shares)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)  # Tighter spacing

        self.name_label = QLabel(self.stock_data["name"])
        self.name_label.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold; font-size: 14px;")

        self.shares_label = QLabel(f"{self.stock_data['amount']} shares")
        self.shares_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")

        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.shares_label)
        self.layout.addLayout(info_layout, 1)  # 1 = stretch factor

        # Price and change percentage
        value_layout = QVBoxLayout()
        value_layout.setSpacing(2)
        value_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Price
        self.price_label = QLabel(f"${self.stock_data['price']}")
        self.price_label.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold; font-size: 15px;")
        self.price_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Change with colored background
        change_value = self.stock_data["change"]
        change_color = ColorPalette.ACCENT_SUCCESS if change_value > 0 else ColorPalette.ACCENT_DANGER
        change_text = f"+{change_value}%" if change_value > 0 else f"{change_value}%"

        self.change_label = QLabel(change_text)
        self.change_label.setStyleSheet(f"""
            color: {change_color}; 
            font-weight: bold; 
            font-size: 13px;
            background-color: {change_color}10; 
            padding: 2px 6px; 
            border-radius: 4px;
        """)
        self.change_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        value_layout.addWidget(self.price_label)
        value_layout.addWidget(self.change_label)
        self.layout.addLayout(value_layout)

    def _get_stock_initials(self, name):
        """Get initials from stock name"""
        parts = name.split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[1][0]}".upper()
        elif name:
            return name[0].upper()
        return "S"

    def _get_stock_color(self, name):
        """Get a deterministic color for a stock based on name"""
        # Use the first letter to determine the color index
        if not name:
            return ColorPalette.ACCENT_PRIMARY

        index = ord(name[0].lower()) - ord('a')
        index = max(0, min(index, len(ColorPalette.CHART_COLORS) - 1))
        return ColorPalette.CHART_COLORS[index]

    def eventFilter(self, obj, event):
        """Handle resize events for responsive design with safeguards"""
        if obj == self and event.type() == QEvent.Resize:
            # Prevent processing during certain states
            if hasattr(self, '_is_handling_resize') and self._is_handling_resize:
                return True

            self._is_handling_resize = True
            try:
                width = self.width()

                # For very narrow widths
                if width < 300:
                    # Hide the icon to save space
                    if hasattr(self, 'icon') and self.icon:
                        self.icon.setVisible(False)
                    # Adjust margins
                    if hasattr(self, 'layout'):
                        self.layout.setContentsMargins(5, 8, 5, 8)
                else:
                    # Show all elements
                    if hasattr(self, 'icon') and self.icon:
                        self.icon.setVisible(True)
                    # Restore margins
                    if hasattr(self, 'layout'):
                        self.layout.setContentsMargins(10, 8, 10, 8)
            finally:
                self._is_handling_resize = False

        return super(StockItem, self).eventFilter(obj, event)


# Optimized owned stocks widget with better space utilization
class OwnedStocksWidget(Card):
    def __init__(self, parent=None):
        super().__init__(title="", parent=parent)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(15)

        # Header with title and filter
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 20, 20, 0)  # Top padding only

        # Title
        title = QLabel("Your Portfolio")
        title.setStyleSheet(f"""
            color: {ColorPalette.TEXT_PRIMARY};
            font-size: 18px;
            font-weight: bold;
        """)

        # Sort dropdown
        sort_combo = QComboBox()
        sort_combo.addItems(["Performance", "Alphabetical", "Position Size", "Recent Change"])
        sort_combo.setFixedWidth(140)
        sort_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {ColorPalette.BG_DARK};
                color: {ColorPalette.TEXT_PRIMARY};
                border: none;
                border-radius: 6px;
                padding: 5px 10px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border: none;
            }}
        """)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(sort_combo)

        main_layout.addLayout(header_layout)

        # Stocks list in a scrollable area for many stocks
        stocks_scroll = QScrollArea()
        stocks_scroll.setWidgetResizable(True)
        stocks_scroll.setFrameShape(QFrame.NoFrame)
        stocks_scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """)

        # Container for stocks
        stocks_container = QWidget()
        stocks_container.setStyleSheet(f"""
            background-color: {ColorPalette.CARD_BG_DARKER};
            border-radius: 8px;
        """)

        stocks_layout = QVBoxLayout(stocks_container)
        stocks_layout.setContentsMargins(0, 0, 0, 0)
        stocks_layout.setSpacing(0)  # No spacing between items

        # Sample stocks data - keep same as screenshot
        stocks = [
            {"name": "Apple Inc.", "amount": "25", "price": "173.45", "change": 1.2},
            {"name": "Microsoft Corp", "amount": "15", "price": "324.62", "change": 0.8},
            {"name": "Google LLC", "amount": "10", "price": "139.78", "change": -0.6},
            {"name": "Amazon.com Inc", "amount": "8", "price": "128.91", "change": 2.3},
            {"name": "Tesla Inc", "amount": "20", "price": "238.79", "change": -1.5}
        ]

        for i, stock in enumerate(stocks):
            item = StockItem(stock, is_last=(i == len(stocks) - 1))
            stocks_layout.addWidget(item)

        # Add action buttons
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(15, 15, 15, 15)

        add_btn = QPushButton("+ Add Stock")
        add_btn.setStyleSheet(GlobalStyle.SECONDARY_BUTTON)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFixedHeight(36)

        view_all_btn = QPushButton("View All")
        view_all_btn.setStyleSheet(GlobalStyle.SECONDARY_BUTTON)
        view_all_btn.setCursor(Qt.PointingHandCursor)
        view_all_btn.setFixedHeight(36)

        action_layout.addWidget(add_btn)
        action_layout.addStretch()
        action_layout.addWidget(view_all_btn)

        stocks_layout.addLayout(action_layout)

        # Set the stocks container as the scroll area widget
        stocks_scroll.setWidget(stocks_container)
        stocks_scroll.setMinimumHeight(350)  # Set minimum height

        main_layout.addWidget(stocks_scroll)

        # Portfolio summary stats at the bottom
        summary_layout = QHBoxLayout()
        summary_layout.setContentsMargins(20, 0, 20, 20)  # Bottom padding
        summary_layout.setSpacing(20)

        # Stats matching the screenshot
        stats = [
            {"label": "Total Value", "value": "$26,489.32"},
            {"label": "Daily Change", "value": "+$312.45 (1.2%)"},
            {"label": "YTD Return", "value": "+18.7%"}
        ]

        for stat in stats:
            stat_widget = QWidget()
            stat_layout = QVBoxLayout(stat_widget)
            stat_layout.setContentsMargins(0, 0, 0, 0)
            stat_layout.setSpacing(3)

            label = QLabel(stat["label"])
            label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")

            value = QLabel(stat["value"])
            value.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-size: 15px; font-weight: bold;")

            stat_layout.addWidget(label)
            stat_layout.addWidget(value)

            summary_layout.addWidget(stat_widget)

        # Add flexible spacer at the end
        summary_layout.addStretch()

        main_layout.addLayout(summary_layout)

        # Set layout to the card
        self.layout.addLayout(main_layout)

# Advanced stock table with sorting
class StockTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Stock", "Price", "Change", "Market Cap"])
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.setStyleSheet(GlobalStyle.TABLE_STYLE)

        # Enhanced column formatting
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)

        # Sample data
        self.populate_sample_data()

    def populate_sample_data(self):
        """Populate table with sample data"""
        stocks = [
            {"name": "AAPL", "price": "173.45", "change": "+1.2", "cap": "2.8T"},
            {"name": "MSFT", "price": "324.62", "change": "+0.8", "cap": "2.4T"},
            {"name": "GOOGL", "price": "139.78", "change": "-0.6", "cap": "1.8T"},
            {"name": "AMZN", "price": "128.91", "change": "+2.3", "cap": "1.3T"},
            {"name": "META", "price": "302.55", "change": "+3.1", "cap": "782B"},
            {"name": "TSLA", "price": "238.79", "change": "-1.5", "cap": "758B"},
            {"name": "NVDA", "price": "437.26", "change": "+0.9", "cap": "1.1T"},
            {"name": "BRK.A", "price": "503,510.00", "change": "+0.3", "cap": "731B"},
        ]

        self.setRowCount(len(stocks))

        for row, stock in enumerate(stocks):
            # Stock name
            name_item = QTableWidgetItem(stock["name"])
            name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            # Price
            price_item = QTableWidgetItem(f"${stock['price']}")
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # Change
            change_value = float(stock["change"])
            change_text = f"{stock['change']}%" if change_value < 0 else f"+{stock['change']}%"
            change_item = QTableWidgetItem(change_text)
            change_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # Color based on value
            if change_value > 0:
                change_item.setForeground(QColor(ColorPalette.ACCENT_SUCCESS))
            else:
                change_item.setForeground(QColor(ColorPalette.ACCENT_DANGER))

            # Market cap
            cap_item = QTableWidgetItem(stock["cap"])
            cap_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # Set items
            self.setItem(row, 0, name_item)
            self.setItem(row, 1, price_item)
            self.setItem(row, 2, change_item)
            self.setItem(row, 3, cap_item)

# Space-efficient AI Advice Card
class AIAdviceCard(Card):
    def __init__(self, parent=None):
        super().__init__(title="", parent=parent)
        self.setStyleSheet(f"""
            background-color: {ColorPalette.BG_CARD};
            border-radius: 12px;
            border: none;
        """)

        # Keep references to sub-widgets for responsive adjustments
        self.content_widgets = []

        # Setup content
        self._setup_ui()

        # Connect resize event
        self.installEventFilter(self)

    def _setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header section with title and AI icon
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        # Title
        title = QLabel("AI Investment Insights")
        title.setStyleSheet(f"""
            color: {ColorPalette.TEXT_PRIMARY};
            font-size: 18px;
            font-weight: bold;
        """)

        header_layout.addWidget(title)
        header_layout.addStretch()

        # AI Icon
        ai_icon = self._create_ai_icon()
        header_layout.addWidget(ai_icon)

        main_layout.addLayout(header_layout)

        # Subtitle with date
        from datetime import datetime

        subtitle_layout = QHBoxLayout()
        subtitle_layout.setSpacing(5)

        insight_label = QLabel("Daily Market Insight")
        insight_label.setStyleSheet(f"""
            color: {ColorPalette.TEXT_PRIMARY};
            font-weight: bold;
            font-size: 14px;
        """)

        date_label = QLabel(datetime.now().strftime("Mar %d, %Y"))
        date_label.setStyleSheet(f"""
            color: {ColorPalette.TEXT_SECONDARY};
            font-size: 14px;
        """)

        subtitle_layout.addWidget(insight_label)
        subtitle_layout.addWidget(date_label)
        subtitle_layout.addStretch()

        main_layout.addLayout(subtitle_layout)

        # Content area with darker background
        content_frame = QFrame()
        content_frame.setStyleSheet(f"""
            background-color: {ColorPalette.CARD_BG_DARKER};
            border-radius: 8px;
        """)
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(12)

        # Main insight title
        insight_title = QLabel("Market Trend Analysis")
        insight_title.setStyleSheet(f"""
            color: {ColorPalette.TEXT_PRIMARY};
            font-weight: bold;
            font-size: 14px;
        """)
        content_layout.addWidget(insight_title)
        self.content_widgets.append(insight_title)

        # Main insight content
        insight_content = QLabel("Market indicators suggest a potential bullish trend in tech stocks. Consider increasing positions in AAPL and MSFT while monitoring inflation data expected tomorrow. Your portfolio shows strong diversification but might benefit from increased exposure to renewable energy sector.")
        insight_content.setWordWrap(True)
        insight_content.setStyleSheet(f"""
            color: {ColorPalette.TEXT_SECONDARY};
            font-size: 13px;
            line-height: 1.4;
        """)
        content_layout.addWidget(insight_content)
        self.content_widgets.append(insight_content)

        # Add key points
        key_points = [
            {"text": "Tech sector showing strong momentum", "color": ColorPalette.ACCENT_SUCCESS},
            {"text": "Watch inflation data release (Mar 3)", "color": ColorPalette.ACCENT_WARNING},
            {"text": "Consider adding renewable energy stocks", "color": ColorPalette.ACCENT_INFO}
        ]

        for point in key_points:
            point_widget = self._create_key_point(point["text"], point["color"])
            content_layout.addWidget(point_widget)
            self.content_widgets.append(point_widget)

        main_layout.addWidget(content_frame)

        # Add button at the bottom
        view_btn = QPushButton("Chat with an AI Advisor")
        view_btn.setCursor(Qt.PointingHandCursor)
        view_btn.setStyleSheet(GlobalStyle.PRIMARY_BUTTON)
        view_btn.setFixedHeight(36)
        main_layout.addWidget(view_btn)

        # Set the main layout
        self.layout.addLayout(main_layout)

    def _create_ai_icon(self):
        """Create the AI icon"""
        icon_container = QFrame()
        icon_container.setFixedSize(36, 36)
        icon_container.setStyleSheet(f"""
            background-color: {ColorPalette.ACCENT_INFO};
            border-radius: 18px;
        """)

        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel()
        icon_label.setFixedSize(20, 20)

        # Create AI icon
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw a simple AI icon (circuit/brain)
        painter.setPen(QPen(Qt.white, 1.5))
        painter.drawEllipse(4, 4, 4, 4)
        painter.drawEllipse(12, 4, 4, 4)
        painter.drawLine(6, 4, 14, 4)
        painter.drawLine(6, 8, 14, 8)
        painter.drawLine(10, 8, 10, 12)
        painter.drawEllipse(8, 12, 4, 4)

        painter.end()

        icon_label.setPixmap(pixmap)
        icon_layout.addWidget(icon_label)

        return icon_container

    def _create_key_point(self, text, color):
        """Create a key point with bullet"""
        point_widget = QWidget()
        point_layout = QHBoxLayout(point_widget)
        point_layout.setContentsMargins(0, 0, 0, 0)
        point_layout.setSpacing(10)

        # Colored bullet
        bullet = QFrame()
        bullet.setFixedSize(6, 6)
        bullet.setStyleSheet(f"""
            background-color: {color};
            border-radius: 3px;
        """)

        # Text
        text_label = QLabel(text)
        text_label.setStyleSheet(f"""
            color: {ColorPalette.TEXT_PRIMARY};
            font-size: 13px;
        """)
        text_label.setWordWrap(True)

        point_layout.addWidget(bullet, 0, Qt.AlignTop)
        point_layout.addWidget(text_label, 1)

        return point_widget

    def eventFilter(self, obj, event):
        """Handle resize events for responsive behavior with proper error handling"""
        if obj == self and event.type() == QEvent.Resize:
            width = self.width()

            # Safety check
            if not hasattr(self, 'content_widgets') or not self.content_widgets:
                return super().eventFilter(obj, event)

            # For very narrow widths
            if width < 300:
                # Hide some content to save space
                for i, widget in enumerate(self.content_widgets):
                    if i > 2:  # Keep title, content, and first key point
                        widget.setVisible(False)
            else:
                # Show all content
                for widget in self.content_widgets:
                    widget.setVisible(True)

        return super().eventFilter(obj, event)

# Sidebar navigation
class Sidebar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(240)
        self.setMaximumWidth(240)
        self.setStyleSheet(f"""
            background-color: {ColorPalette.BG_SIDEBAR};
            border-right: 1px solid {ColorPalette.BORDER_DARK};
        """)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 30, 15, 30)
        layout.setSpacing(8)

        # App title and logo
        title_layout = QHBoxLayout()

        logo_label = QLabel()
        logo_label.setFixedSize(32, 32)

        # Create logo
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw gradient circle
        gradient = QLinearGradient(0, 0, 32, 32)
        gradient.setColorAt(0, QColor(ColorPalette.ACCENT_PRIMARY))
        gradient.setColorAt(1, QColor(ColorPalette.ACCENT_INFO))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(2, 2, 28, 28)

        # Draw "S" in the center
        painter.setPen(QPen(Qt.white))
        font = QFont()
        font.setBold(True)
        font.setPointSize(14)
        painter.setFont(font)
        painter.drawText(QRect(0, 0, 32, 32), Qt.AlignCenter, "S")

        painter.end()
        logo_label.setPixmap(pixmap)

        # App name
        app_name = QLabel("StockMaster")
        app_name.setStyleSheet(f"""
            color: {ColorPalette.TEXT_PRIMARY};
            font-size: 18px;
            font-weight: bold;
        """)

        title_layout.addWidget(logo_label)
        title_layout.addWidget(app_name)
        title_layout.addStretch()

        layout.addLayout(title_layout)
        layout.addSpacing(30)

        # Navigation buttons
        self.dashboard_btn = SidebarButton("Icons/icons8-dashboard-50.png", "Dashboard", is_active=True)
        self.portfolio_btn = SidebarButton("Icons/icons8-portofolio-file-50.png", "Portfolio")
        self.transactions_btn = SidebarButton("Icons/icons8-transactions-50.png", "Transactions")
        self.ai_chat = SidebarButton("Icons/icons8-ai-50 (1).png", "AI Advisor")
        self.settings_btn = SidebarButton("Icons/icons8-settings-50.png", "Settings")

        # Add buttons to layout
        layout.addWidget(self.dashboard_btn)
        layout.addWidget(self.portfolio_btn)
        layout.addWidget(self.transactions_btn)
        layout.addWidget(self.ai_chat)
        layout.addSpacing(20)

        # Add a separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"background-color: {ColorPalette.BORDER_LIGHT};")
        separator.setFixedHeight(1)
        layout.addWidget(separator)
        layout.addSpacing(20)

        layout.addWidget(self.settings_btn)
        layout.addStretch()

        # User profile at bottom
        profile_layout = QHBoxLayout()

        # Avatar
        avatar = AvatarWidget("John Doe", size=36)

        # User info
        user_layout = QVBoxLayout()
        user_layout.setSpacing(2)

        user_name = QLabel("John Doe")
        user_name.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold; background: transparent;")

        user_email = QLabel("john.doe@example.com")
        user_email.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 11px; background: transparent;")

        user_layout.addWidget(user_name)
        user_layout.addWidget(user_email)

        profile_layout.addWidget(avatar)
        profile_layout.addLayout(user_layout)
        profile_layout.addStretch()

        profile_btn = QPushButton()
        profile_btn.setCursor(Qt.PointingHandCursor)
        profile_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                text-align: left;
                padding: 15px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        btn_layout = QVBoxLayout(profile_btn)
        btn_layout.setContentsMargins(10, 8, 10, 8)
        btn_layout.addLayout(profile_layout)
        # Aling to the left and center
        btn_layout.setAlignment(profile_layout, Qt.AlignLeft | Qt.AlignVCenter)

        # Store a reference to the button
        self.profile_btn = profile_btn

        # Then add the button to layout instead of the profile_layout
        layout.addWidget(profile_btn)

# Improved search bar
class SearchBar(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Search stocks, news, analysis...")
        self.setStyleSheet(GlobalStyle.INPUT_STYLE)
        self.setFixedHeight(40)
        self.setMinimumWidth(250)

        # Add search icon
        self.addAction(self.create_search_icon(), QLineEdit.LeadingPosition)

    def create_search_icon(self):
        """Create a search icon"""
        size = 16
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw search icon
        painter.setPen(QPen(QColor(ColorPalette.TEXT_SECONDARY), 2))
        painter.setBrush(Qt.NoBrush)

        # Draw circle
        painter.drawEllipse(2, 2, 8, 8)

        # Draw handle
        painter.drawLine(12, 12, 9, 9)

        painter.end()
        return QIcon(pixmap)

# Responsive header with improved styling
class Header(QFrame):
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

        # Page title and welcome message
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)

        title = QLabel("Dashboard")
        title.setStyleSheet(GlobalStyle.HEADER_STYLE)

        welcome_message = QLabel("Welcome back, John")
        welcome_message.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 14px;")

        title_layout.addWidget(title)
        title_layout.addWidget(welcome_message)

        # Search bar - will adjust width based on available space
        search = SearchBar()
        search.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Actions section with notification and profile
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(15)

        # Notification button with unread indicator
        notif_btn = QPushButton()
        notif_btn.setFixedSize(42, 42)
        notif_btn.setCursor(Qt.PointingHandCursor)
        notif_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ColorPalette.BG_CARD};
                border: none;
                border-radius: 21px;
            }}
            QPushButton:hover {{
                background-color: {ColorPalette.BG_DARK};
            }}
        """)

        # Notification icon with unread indicator
        notif_icon_container = QWidget()
        notif_icon_container.setFixedSize(42, 42)
        notif_container_layout = QVBoxLayout(notif_icon_container)
        notif_container_layout.setContentsMargins(0, 0, 0, 0)
        notif_container_layout.setAlignment(Qt.AlignCenter)

        # Create bell icon
        notif_icon = QLabel()
        notif_icon.setFixedSize(18, 18)
        bell_pixmap = QPixmap(18, 18)
        bell_pixmap.fill(Qt.transparent)

        bell_painter = QPainter(bell_pixmap)
        bell_painter.setRenderHint(QPainter.Antialiasing)
        bell_painter.setPen(QPen(QColor(ColorPalette.TEXT_PRIMARY), 1.5))

        # Draw bell shape
        bell_path = QPainterPath()
        bell_path.moveTo(9, 2)
        bell_path.lineTo(9, 3)
        bell_path.arcTo(5, 3, 8, 3, 180, 180)
        bell_path.lineTo(15, 13)
        bell_path.lineTo(3, 13)
        bell_path.lineTo(5, 6)
        bell_path.closeSubpath()

        bell_painter.drawPath(bell_path)
        bell_painter.drawLine(7, 15, 11, 15)

        # Add unread notification dot
        bell_painter.setPen(Qt.NoPen)
        bell_painter.setBrush(QColor(ColorPalette.ACCENT_DANGER))
        bell_painter.drawEllipse(13, 2, 5, 5)

        bell_painter.end()
        notif_icon.setPixmap(bell_pixmap)
        notif_container_layout.addWidget(notif_icon)

        # Add icon container to button
        notif_layout = QVBoxLayout(notif_btn)
        notif_layout.setContentsMargins(0, 0, 0, 0)
        notif_layout.setAlignment(Qt.AlignCenter)
        notif_layout.addWidget(notif_icon_container)

        # User profile button with improved styling
        profile_btn = QPushButton()
        profile_btn.setFixedSize(42, 42)
        profile_btn.setCursor(Qt.PointingHandCursor)
        profile_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ColorPalette.BG_CARD};
                border: none;
                border-radius: 21px;
            }}
            QPushButton:hover {{
                background-color: {ColorPalette.BG_DARK};
            }}
        """)

        # Add avatar to button
        avatar = AvatarWidget("John Doe", size=36)
        avatar_layout = QVBoxLayout(profile_btn)
        avatar_layout.setContentsMargins(0, 0, 0, 0)
        avatar_layout.setAlignment(Qt.AlignCenter)
        avatar_layout.addWidget(avatar)

        actions_layout.addWidget(notif_btn)
        actions_layout.addWidget(profile_btn)

        # Add all elements to main layout - responsive arrangement
        layout.addLayout(title_layout)
        layout.addStretch(1)  # Push search to center
        layout.addWidget(search, 2)  # Give search 2x the stretch
        layout.addStretch(1)  # Push actions to right
        layout.addLayout(actions_layout)

        # Install event filter to handle resizing
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        """Handle resize events to adjust layout for different screen sizes"""
        if obj == self and event.type() == QEvent.Resize:
            width = self.width()
            # You could adjust layout based on width here
            # For example, hide welcome message or adjust spacing
        return super().eventFilter(obj, event)

# Improved Transaction Item with better styling
class TransactionItem(QFrame):
    def __init__(self, transaction_data, is_last=False):
        super().__init__()
        self.transaction_data = transaction_data
        self.is_last = is_last

        # Style - only use divider when needed
        border_style = "none" if is_last else f"1px solid {ColorPalette.BORDER_DARK}"
        self.setStyleSheet(f"""
            background-color: transparent;
            border: none;
            border-bottom: {border_style};
        """)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(70)

        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Icon based on transaction type with improved design
        icon_text = "B" if transaction_data["type"] == "buy" else "S"
        icon_color = ColorPalette.ACCENT_SUCCESS if transaction_data["type"] == "buy" else ColorPalette.ACCENT_DANGER
        icon = AvatarWidget(icon_text, size=40, background_color=icon_color)

        # Name and date info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        name_label = QLabel(transaction_data["name"])
        name_label.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold; font-size: 14px; border: none;")

        date_label = QLabel(transaction_data["date"])
        date_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px; border: none;")

        info_layout.addWidget(name_label)
        info_layout.addWidget(date_label)

        # Price and shares in vertical layout
        value_layout = QVBoxLayout()
        value_layout.setSpacing(4)
        value_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Price
        price_label = QLabel(f"${transaction_data['price']}")
        price_label.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold; font-size: 16px; border: none;")
        price_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Shares
        shares_text = f"{transaction_data['shares']} shares"
        shares_color = ColorPalette.ACCENT_SUCCESS if transaction_data["type"] == "buy" else ColorPalette.ACCENT_DANGER
        shares_label = QLabel(shares_text)
        shares_label.setStyleSheet(f"""
            color: {shares_color}; 
            border: none;
            font-size: 14px;
            
            padding: 2px 6px;
            border-radius: 4px;
            
        """)
        shares_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        value_layout.addWidget(price_label)
        value_layout.addWidget(shares_label)

        # Add all elements to layout
        layout.addWidget(icon)
        layout.addLayout(info_layout, 1)
        layout.addLayout(value_layout)

# Improved responsive dashboard layout
class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Header with welcome message
        header = Header()
        layout.addWidget(header)

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

        # Container for all dashboard content
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(20)  # Reduced spacing between sections

        # Create the dashboard content
        self._setup_portfolio_section()
        self._setup_portfolio_details_section()

        # Set the scroll area widget and add to main layout
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)

        # Install event filter to handle resize events
        self.installEventFilter(self)

    def _setup_portfolio_section(self):
        """Setup the portfolio overview section with portfolio value and AI advice"""
        section = QWidget()
        section_layout = QHBoxLayout(section)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(20)

        # Portfolio summary card - reduced emphasis
        self.portfolio_card = PortfolioSummaryCard(
            title="Portfolio Value",
            balance="$1,234,567",
            change="+4.5%"
        )
        # Reduce the minimum height and make it less dominant
        self.portfolio_card.setMinimumHeight(200)  # Reduced from previous height
        self.portfolio_card.setMinimumWidth(200)  # Reduced width
        self.portfolio_card.setMaximumHeight(450)  # Limit height to avoid stretching


        # AI Advice card with adjusted size
        self.ai_advice = AIAdviceCard()
        self.ai_advice.setMinimumHeight(200)  # Consistent height with portfolio card
        self.ai_advice.setMaximumHeight(450)  # Limit height to avoid stretching

        # Adjust stretch factors to make them more balanced
        section_layout.addWidget(self.portfolio_card, 1)  # Slightly less dominant
        section_layout.addWidget(self.ai_advice, 1)  # Equal space

        self.content_layout.addWidget(section)

        # Store a reference for responsive adjustments
        self.portfolio_section = section
        self.portfolio_section_layout = section_layout

    def _setup_portfolio_details_section(self):
        """Setup the portfolio details section with owned stocks and recent activity"""
        section = QWidget()
        section_layout = QHBoxLayout(section)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(20)

        # Owned stocks widget - reduced size
        self.owned_stocks = OwnedStocksWidget()
        self.owned_stocks.setMinimumHeight(350)

        # Recent activity card - similar sizing
        self.recent_activity = Card("Recent Activity")
        self.recent_activity.setMinimumHeight(350)

        # Add content to recent activity
        recent_layout = QVBoxLayout()
        recent_layout.setContentsMargins(20, 20, 20, 20)
        recent_layout.setSpacing(10)

        # Add transaction items
        transactions = [
            {"type": "buy", "name": "Apple Inc.", "shares": 10, "price": "1,734.50", "date": "Today, 10:30 AM"},
            {"type": "sell", "name": "Tesla Inc", "shares": 5, "price": "1,193.95", "date": "Yesterday, 3:45 PM"},
            {"type": "buy", "name": "Microsoft Corp", "shares": 8, "price": "2,596.96", "date": "Feb 25, 2025"}
        ]

        # Create transaction items with a more flexible approach
        transaction_container = QWidget()
        transaction_layout = QVBoxLayout(transaction_container)
        transaction_layout.setContentsMargins(0, 0, 0, 0)
        transaction_layout.setSpacing(0)

        for i, transaction in enumerate(transactions):
            item = TransactionItem(transaction, is_last=(i == len(transactions) - 1))
            transaction_layout.addWidget(item)

        # Add spacer to push transactions to the top if fewer than max
        transaction_layout.addStretch(1)

        # Wrap transaction container in a scroll area
        transactions_scroll = QScrollArea()
        transactions_scroll.setWidgetResizable(True)
        transactions_scroll.setFrameShape(QFrame.NoFrame)
        transactions_scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """)
        transactions_scroll.setWidget(transaction_container)
        transactions_scroll.setMinimumHeight(250)  # Ensure a consistent minimum height

        # Add scroll area to recent layout
        recent_layout.addWidget(transactions_scroll)

        # Add "View All" button
        view_all_btn = QPushButton("View All Transactions")
        view_all_btn.setStyleSheet(GlobalStyle.SECONDARY_BUTTON)
        recent_layout.addWidget(view_all_btn)

        # Add the layout to the card
        self.recent_activity.layout.addLayout(recent_layout)

        # Add widgets with balanced stretch
        section_layout.addWidget(self.owned_stocks, 1)
        section_layout.addWidget(self.recent_activity, 1)

        self.content_layout.addWidget(section)

        # Store references for responsive adjustments
        self.details_section = section
        self.details_section_layout = section_layout

    def eventFilter(self, obj, event):
        """Handle resize events to adjust layout responsively"""
        if obj == self and event.type() == QEvent.Resize:
            self._adjust_responsive_layout()
        return super().eventFilter(obj, event)

    # Add this improved method to the DashboardPage class
    def _adjust_responsive_layout(self):
        """Improved responsive layout adjustment to prevent crashes"""
        # Avoid recursive calls
        if hasattr(self, '_is_adjusting') and self._is_adjusting:
            return

        self._is_adjusting = True

        try:
            width = self.width()

            # For smaller screens (tablet and below)
            should_be_vertical = width < 900

            # Only change direction if needed
            if should_be_vertical and self.portfolio_section_layout.direction() != QBoxLayout.TopToBottom:
                # Safer direction change that avoids removing and re-adding items
                QBoxLayout.setDirection(self.portfolio_section_layout, QBoxLayout.TopToBottom)
                QBoxLayout.setDirection(self.details_section_layout, QBoxLayout.TopToBottom)

                # Adjust margins to use more screen space
                self.content_layout.setContentsMargins(10, 10, 10, 10)

                # Make sure widgets stack nicely
                for widget in [self.portfolio_card, self.ai_advice,
                               self.owned_stocks, self.recent_activity]:
                    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            elif not should_be_vertical and self.portfolio_section_layout.direction() != QBoxLayout.LeftToRight:
                # For larger screens, use horizontal layout
                QBoxLayout.setDirection(self.portfolio_section_layout, QBoxLayout.LeftToRight)
                QBoxLayout.setDirection(self.details_section_layout, QBoxLayout.LeftToRight)

                # Restore margins
                self.content_layout.setContentsMargins(0, 0, 0, 0)

                # Restore size policies
                for widget in [self.portfolio_card, self.ai_advice,
                               self.owned_stocks, self.recent_activity]:
                    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        except Exception as e:
            print(f"Error in DashboardPage._adjust_responsive_layout: {e}")
        finally:
            # Use a timer to reset the flag to prevent deadlocks
            QTimer.singleShot(100, self._reset_adjusting_flag)

    def _reset_adjusting_flag(self):
        """Safely reset the adjusting flag after a delay"""
        self._is_adjusting = False


# Responsive main application window
class MainWindow(QWidget):
    def __init__(self, user_email=None):
        super().__init__()
        self.setWindowTitle("StockMaster Pro")
        self.setMinimumSize(900, 650)  # Reduced minimum size
        print("User email:", user_email)


        # Track sidebar state for narrow screens
        self.sidebar_visible = True

        # Set dark theme with improved styling
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {ColorPalette.BG_DARK};
                color: {ColorPalette.TEXT_PRIMARY};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QScrollBar:vertical {{
                background: {ColorPalette.BG_DARK};
                width: 8px;  /* Thinner scrollbar */
                margin: 0px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {ColorPalette.BORDER_LIGHT};
                min-height: 30px;
                border-radius: 4px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                background: {ColorPalette.BG_DARK};
                height: 8px;  /* Thinner scrollbar */
                margin: 0px;
                border-radius: 4px;
            }}
            QScrollBar::handle:horizontal {{
                background: {ColorPalette.BORDER_LIGHT};
                min-width: 30px;
                border-radius: 4px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            /* Tooltip styling */
            QToolTip {{
                background-color: {ColorPalette.BG_CARD};
                color: {ColorPalette.TEXT_PRIMARY};
                border: none;
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
            }}
        """)

        # Load fonts
        load_fonts()

        # Main layout
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        self.main_layout.addWidget(self.sidebar)

        self._connect_sidebar_buttons()

        # Content area with shadow separation
        self.content_area = QFrame()
        self.content_area.setStyleSheet(f"""
            background-color: {ColorPalette.BG_DARK}; 
            border: none;
        """)

        # Add subtle left shadow to content area
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(-2, 0)
        self.content_area.setGraphicsEffect(shadow)

        # Content layout with responsive margins
        self.content_layout = QVBoxLayout(self.content_area)

        # Header for mobile to show menu button
        self.mobile_header = self._create_mobile_header()
        self.content_layout.addWidget(self.mobile_header)
        self.mobile_header.setVisible(False)  # Initially hidden

        # Dashboard page
        self.dashboard = DashboardPage()
        self.content_layout.addWidget(self.dashboard)

        self.main_layout.addWidget(self.content_area)

        # Connect to resize event to handle responsive layouts
        self.installEventFilter(self)
        self._adjust_responsive_layout()

    def _create_mobile_header(self):
        """Create a mobile header with menu button for narrow screens"""
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet(f"""
            background-color: {ColorPalette.BG_SIDEBAR};
            border: none;
        """)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(15, 5, 15, 5)

        # Menu button
        menu_btn = QPushButton()
        menu_btn.setFixedSize(40, 40)
        menu_btn.setCursor(Qt.PointingHandCursor)
        menu_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ColorPalette.BG_CARD};
                border: none;
                border-radius: 20px;
                padding: 8px;
            }}
            QPushButton:hover {{
                background-color: {ColorPalette.ACCENT_PRIMARY};
            }}
        """)

        # Add hamburger icon
        menu_icon = QLabel()
        menu_icon.setFixedSize(24, 24)
        menu_pixmap = QPixmap(24, 24)
        menu_pixmap.fill(Qt.transparent)

        painter = QPainter(menu_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor(ColorPalette.TEXT_PRIMARY), 2))

        # Draw three lines
        painter.drawLine(4, 6, 20, 6)
        painter.drawLine(4, 12, 20, 12)
        painter.drawLine(4, 18, 20, 18)

        painter.end()
        menu_icon.setPixmap(menu_pixmap)

        icon_layout = QVBoxLayout(menu_btn)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(menu_icon)

        # Connect button to toggle sidebar
        menu_btn.clicked.connect(self._toggle_sidebar)

        # Title
        title = QLabel("StockMaster")
        title.setStyleSheet(f"""
            color: {ColorPalette.TEXT_PRIMARY};
            font-size: 18px;
            font-weight: bold;
        """)

        layout.addWidget(menu_btn)
        layout.addWidget(title)
        layout.addStretch()

        return header

    def _toggle_sidebar(self):
        """Toggle sidebar visibility on narrow screens"""
        self.sidebar_visible = not self.sidebar_visible
        self.sidebar.setVisible(self.sidebar_visible)
        self._adjust_responsive_layout()

    def eventFilter(self, obj, event):
        """Handle resize events to adjust layouts for responsiveness"""
        if obj == self and event.type() == QEvent.Resize:
            self._adjust_responsive_layout()
        return super().eventFilter(obj, event)


    def _adjust_responsive_layout(self):
        """Improved layout adjustment to prevent crashes"""
        # Avoid recursive calls with better protection
        if hasattr(self, '_is_adjusting') and self._is_adjusting:
            return

        self._is_adjusting = True

        try:
            width = self.width()

            # Very simple mobile/desktop switch with minimal adjustments
            is_mobile = width < 900

            # Mobile header visibility - only change if needed
            if self.mobile_header.isVisible() != is_mobile:
                self.mobile_header.setVisible(is_mobile)

            # Sidebar visibility for very narrow screens - only change if needed
            if width < 600 and self.sidebar_visible and is_mobile:
                self.sidebar_visible = False
                self.sidebar.setVisible(False)
            elif width >= 900 and not self.sidebar_visible:
                self.sidebar_visible = True
                self.sidebar.setVisible(True)

            # Simplified padding adjustment - only change if needed
            current_margins = self.content_layout.contentsMargins()
            if is_mobile and (current_margins.left() != 10 or current_margins.right() != 10):
                self.content_layout.setContentsMargins(10, 0, 10, 10)
            elif not is_mobile and (current_margins.left() != 20 or current_margins.right() != 20):
                self.content_layout.setContentsMargins(20, 0, 20, 20)
        except Exception as e:
            print(f"Error in MainWindow._adjust_responsive_layout: {e}")
        finally:
            # Use a timer to reset the flag to prevent deadlocks
            QTimer.singleShot(100, self._reset_adjusting_flag)

    def _reset_adjusting_flag(self):
        """Safely reset the adjusting flag after a delay"""
        self._is_adjusting = False

    # Add this to MainWindow class

    # Add this improved resizeEvent handler to MainWindow
    def resizeEvent(self, event):
        """Improved resize event handler with debouncing"""
        # First call the parent implementation
        super().resizeEvent(event)

        # Debounce the resize with a timer
        if hasattr(self, '_resize_timer') and self._resize_timer.isActive():
            self._resize_timer.stop()

        if not hasattr(self, '_resize_timer'):
            self._resize_timer = QTimer()
            self._resize_timer.setSingleShot(True)
            self._resize_timer.timeout.connect(self._delayed_resize_handler)

        # Start the timer - only handle resize after the user stops resizing for 150ms
        self._resize_timer.start(150)

    def _delayed_resize_handler(self):
        """Handle resize after a short delay to avoid rapid repeated calls"""
        # Reset any stuck flags
        self._is_adjusting = False
        if hasattr(self.dashboard, '_is_adjusting'):
            self.dashboard._is_adjusting = False

        # Now handle the resize
        self._adjust_responsive_layout()

    def _force_layout_update(self):
        """Force a complete layout update to unstick any problematic layouts"""
        try:
            # Reset adjusting flags
            if hasattr(self, '_is_adjusting'):
                self._is_adjusting = False

            # Safely update dashboard layout
            if hasattr(self, 'dashboard'):
                # Reset dashboard adjusting flag
                if hasattr(self.dashboard, '_is_adjusting'):
                    self.dashboard._is_adjusting = False

                # Safely reset section layouts
                if hasattr(self.dashboard, 'portfolio_section_layout'):
                    self._safe_reset_layout(self.dashboard.portfolio_section_layout)

                if hasattr(self.dashboard, 'details_section_layout'):
                    self._safe_reset_layout(self.dashboard.details_section_layout)

                # Trigger responsive layout adjustment
                self.dashboard._adjust_responsive_layout()

            # Force geometry updates
            self.updateGeometry()
            if hasattr(self, 'content_area'):
                self.content_area.updateGeometry()

            # Force a complete redraw
            self.update()

        except Exception as e:
            print(f"Error in _force_layout_update: {e}")

    # Replace your _safe_reset_layout method with this safer version
    def _safe_reset_layout(self, layout):
        """Safer method to reset a layout's direction"""
        try:
            # Instead of removing and re-adding items, use the static method
            # This avoids disturbing the widget hierarchy
            current_direction = layout.direction()
            target_direction = QBoxLayout.LeftToRight

            if current_direction != target_direction:
                QBoxLayout.setDirection(layout, target_direction)

        except Exception as e:
            print(f"Error in _safe_reset_layout: {e}")


    def _connect_sidebar_buttons(self):
        """Connect sidebar buttons to their actions"""
        # AI Advisor button - opens a separate window
        self.sidebar.ai_chat.clicked.connect(self._open_ai_advisor)
        self.sidebar.portfolio_btn.clicked.connect(self._open_portfolio)
        self.sidebar.transactions_btn.clicked.connect(self._open_transactions)
        self.sidebar.profile_btn.clicked.connect(self._open_profile)

        # Connect other buttons as needed if you want

    def _open_ai_advisor(self):
        """Open the AI Advisor window"""
        # Store a reference to prevent garbage collection
        self.ai_window = AIAdvisorWindow()
        self.ai_window.show()
    def _open_portfolio(self):
        """Open the Portfolio window"""
        # Store a reference to prevent garbage collection
        self.portfolio_window = PortfolioPage()
        self.portfolio_window.show()
    def _open_transactions(self):
        """Open the Transactions window"""
        # Store a reference to prevent garbage collection
        self.transactions_window = TransactionsPage()
        self.transactions_window.show()
    def _open_profile(self):
        """Open the Profile window"""
        # Store a reference to prevent garbage collection
        self.profile_window = ProfilePage()
        self.profile_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())