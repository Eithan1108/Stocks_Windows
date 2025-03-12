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
from View.stock_search_window import StockSearchWindow
from View.shared_components import ColorPalette, GlobalStyle, AvatarWidget
from View.protofilio_view import PortfolioPage
from View.transaction_view import TransactionsPage
from View.profile_page import ProfilePage
from PySide6.QtCore import (Qt, QSize, QRect, QTimer, QPointF, QEvent, QPoint, QEasingCurve,
                            QPropertyAnimation, Signal, QUrl, QMargins)
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PySide6.QtSvg import QSvgRenderer




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
class PortfolioSummaryCard(QFrame):
    def __init__(self, user_stocks=None, stocks_data=None, parent=None):
        super().__init__(parent)
        self.user_stocks = user_stocks or []
        self.stocks_data = stocks_data or {}
        
        # Calculate portfolio values
        self.calculate_portfolio_data()
        
        # Get gradient colors for theme
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

    def calculate_portfolio_data(self):
        """Calculate portfolio value, change, and historical trend"""
        self.total_value = 0
        self.total_previous_value = 0
        self.weighted_change_pct = 0
        
        # Calculate current and previous portfolio values
        if self.user_stocks and self.stocks_data:
            for stock in self.user_stocks:
                symbol = stock.get('stockSymbol')
                quantity = float(stock.get('quantity', 0))
                
                if symbol in self.stocks_data:
                    # Current value
                    current_price = self.stocks_data[symbol].get('currentPrice', 0)
                    self.total_value += current_price * quantity
                    
                    # Previous value (for change calculation)
                    previous_price = self.stocks_data[symbol].get('previousClose', 0)
                    self.total_previous_value += previous_price * quantity
        
        # Calculate percentage change
        if self.total_previous_value > 0:
            self.weighted_change_pct = ((self.total_value - self.total_previous_value) / 
                                        self.total_previous_value) * 100
        
        # Format values for display
        self.balance = f"${self.total_value:,.2f}"
        self.change = f"{self.weighted_change_pct:+.2f}%" if self.weighted_change_pct != 0 else "0.00%"
        
        # Generate trend data based on stock changes
        self.trend_data = self._generate_trend_data()

    def _generate_trend_data(self):
        """Generate trend data for the chart based on actual stock data"""
        points = []
        
        # If we have historical data, we could use it here
        # For now, we'll generate semi-realistic data based on the current change
        
        num_points = 40
        base = 100
        
        # Use the actual portfolio change to influence the trend
        change_factor = self.weighted_change_pct / 100
        
        # Generate points with a trend that ends with our actual change percentage
        import random
        
        # Create a more natural curve that ends with our current change
        total_change = change_factor * base
        avg_step = total_change / num_points
        
        # Start with base value
        current = base
        points.append(current)
        
        # Generate intermediate points with controlled randomness
        for i in range(1, num_points):
            # More randomness in the middle, more directed at the end
            progress = i / num_points
            randomness = 1 - (progress * 0.7)  # Reduce randomness as we approach the end
            
            # Step size combines the trend and randomness
            step = avg_step + (random.uniform(-2, 2) * randomness)
            
            # Adjust to ensure we end up close to the target change
            remaining_steps = num_points - i
            remaining_change = (base + total_change) - current
            correction = (remaining_change / remaining_steps) * 0.3
            
            # Apply step with correction
            current += step + correction
            
            # Ensure we don't go too low
            current = max(current, base * 0.5)
            
            points.append(current)
            
        return points

    def _setup_ui(self):
        """Setup the card UI with better space utilization"""
        # Main layout to organize content
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Top section with value and change
        top_section = QHBoxLayout()
        top_section.setSpacing(15)

        # Value/Change section (left)
        value_section = QVBoxLayout()
        value_section.setSpacing(5)

        # Title label
        title_label = QLabel("Portfolio Value")
        title_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            background: transparent;
        """)
        value_section.addWidget(title_label)

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
        is_positive = not change_str.startswith("-")
        bg_opacity = "0.2" if is_positive else "0.15"

        change_label = QLabel(change_str)
        change_label.setStyleSheet(f"""
            color: white;
            font-size: 16px;
            font-weight: bold;
            background: rgba(255, 255, 255, {bg_opacity});
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

        # Initial graph update
        self._update_graph()

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

                    # Draw fill with gradient - adjust opacity based on change
                    is_positive = self.weighted_change_pct >= 0
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
            
    def update_data(self, user_stocks=None, stocks_data=None):
        """Update the card with new data"""
        if user_stocks is not None:
            self.user_stocks = user_stocks
        if stocks_data is not None:
            self.stocks_data = stocks_data
            
        # Recalculate portfolio data
        self.calculate_portfolio_data()
        
        # Update UI elements
        if hasattr(self, 'balance_label'):
            self.balance_label.setText(self.balance)
        if hasattr(self, 'change_label'):
            self.change_label.setText(self.change)
            
        # Update graph
        self._update_graph()


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
        #Pick random color from color palette
        random_color = random.choice(ColorPalette.CHART_COLORS)
        color = self._get_stock_color(self.stock_data["name"])
        self.icon = AvatarWidget(initials, size=38, background_color=random_color)  # Slightly smaller
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
# Optimized owned stocks widget with better space utilization and dynamic height
class OwnedStocksWidget(Card):
    def __init__(self, parent=None, stocks=None, stocks_the_user_has=None):
        super().__init__(title="", parent=parent)
        self.stocks = stocks or []
        self.stocks_the_user_has = stocks_the_user_has or []

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

        

        header_layout.addWidget(title)
        header_layout.addStretch()

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

        # Set up stocks list
        stocks_layout = QVBoxLayout(stocks_container)
        stocks_layout.setContentsMargins(0, 0, 0, 0)
        stocks_layout.setSpacing(0)
        
        # Calculate height based on number of stocks
        # Each stock item is 65px high, minimum height for empty state
        min_content_height = 100  # Minimum height for empty state
        stock_item_height = 65    # Height of each stock item
        action_height = 66        # Height of action buttons section (15px padding top/bottom + 36px button height)
        
        if not self.stocks:
            # Show empty state
            empty_label = QLabel("You don't have any stocks yet")
            empty_label.setStyleSheet(f"""
                color: {ColorPalette.TEXT_SECONDARY};
                font-size: 14px;
                text-align: center;
                padding: 30px;
            """)
            empty_label.setAlignment(Qt.AlignCenter)
            stocks_layout.addWidget(empty_label)
            content_height = min_content_height
        else:
            # Show actual stocks
            for i, stock in enumerate(self.stocks):
                item = StockItem(stock, is_last=(i == len(self.stocks) - 1))
                stocks_layout.addWidget(item)
            
            # Calculate content height based on number of stocks
            content_height = len(self.stocks) * stock_item_height

        # Add action buttons
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(15, 15, 15, 15)

        add_btn = QPushButton("+ Add Stock")
        add_btn.setStyleSheet(GlobalStyle.SECONDARY_BUTTON)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFixedHeight(36)
        self.add_btn = add_btn

        view_all_btn = QPushButton("View All")
        view_all_btn.setStyleSheet(GlobalStyle.SECONDARY_BUTTON)
        view_all_btn.setCursor(Qt.PointingHandCursor)
        view_all_btn.setFixedHeight(36)

        self.view_all_btn = view_all_btn

        action_layout.addWidget(add_btn)
        action_layout.addStretch()
        action_layout.addWidget(view_all_btn)

        stocks_layout.addLayout(action_layout)

        # Set the stocks container as the scroll area widget
        stocks_scroll.setWidget(stocks_container)
        
        # Calculate total content height: content + action buttons + some buffer
        total_height = content_height + action_height + 20
        
        # Set a reasonable height - not too large when we have few stocks
        ideal_height = min(350, max(180, total_height))
        stocks_scroll.setMinimumHeight(ideal_height)
        stocks_scroll.setMaximumHeight(ideal_height)

        main_layout.addWidget(stocks_scroll)

        # Portfolio summary stats at the bottom
        summary_layout = QHBoxLayout()
        summary_layout.setContentsMargins(20, 0, 20, 20)  # Bottom padding
        summary_layout.setSpacing(20)

        

        # Add flexible spacer at the end
        summary_layout.addStretch()

        main_layout.addLayout(summary_layout)

        # Set layout to the card
        self.layout.addLayout(main_layout)

    def update_stocks(self, new_stocks):
        """Update the widget with new stock data"""
        self.stocks = new_stocks
        
        # Clear existing stock items
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if isinstance(widget, StockItem):
                self.layout.removeWidget(widget)
                widget.deleteLater()
        
        # Add new stock items
        if not self.stocks:
            # Show empty state
            empty_label = QLabel("You don't have any stocks yet")
            empty_label.setStyleSheet(f"""
                color: {ColorPalette.TEXT_SECONDARY};
                font-size: 14px;
                text-align: center;
                padding: 30px;
            """)
            empty_label.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(empty_label)
        else:
            # Show actual stocks
            for i, stock in enumerate(self.stocks):
                item = StockItem(stock, is_last=(i == len(self.stocks) - 1))
                self.layout.addWidget(item)




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
        self.view_button = view_btn

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
    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.setMinimumWidth(240)
        self.setMaximumWidth(240)
        self.setStyleSheet(f"""
            background-color: {ColorPalette.BG_SIDEBAR};
            border-right: 1px solid {ColorPalette.BORDER_DARK};
        """)

        self.user = user

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
        self.all_stocks = SidebarButton("Icons/icons8-invest-50.png", "All Stocks")
        self.settings_btn = SidebarButton("Icons/icons8-settings-50.png", "Settings")

        # Add buttons to layout
        layout.addWidget(self.dashboard_btn)
        layout.addWidget(self.portfolio_btn)
        layout.addWidget(self.transactions_btn)
        layout.addWidget(self.ai_chat)
        layout.addWidget(self.all_stocks)
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

        user_name = self.user.get('username', 'Guest User') if self.user else 'Guest User'
        user_email = self.user.get('email', '') if self.user else ''
        profile_pic_url = self.user.get('profilePicture', None)

        # Avatar
        avatar_content = profile_pic_url if profile_pic_url else user_name
        avatar = AvatarWidget(avatar_content, size=36)

        # User info
        user_layout = QVBoxLayout()
        user_layout.setSpacing(2)

        user_name = QLabel(user_name)
        user_name.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold; background: transparent;")

        user_email = QLabel(user_email)
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

class AvatarWidget(QFrame):
    def __init__(self, text_or_url, size=40, background_color=None):
        super().__init__()
        self.text = text_or_url if not text_or_url.startswith("http") else ""
        self.image_url = text_or_url if text_or_url.startswith("http") else None
        self.size = size
        self.bg_color = background_color or ColorPalette.ACCENT_PRIMARY
        
        # Set fixed size
        self.setFixedSize(size, size)
        
        # Style the widget as a circle
        self.setStyleSheet(f"""
            background-color: {self.bg_color};
            border-radius: {size // 2}px;
            color: white;
            font-weight: bold;
        """)
        
        # If we have an image URL, load it
        if self.image_url:
            self.load_image_from_url()
        
        # Setup layout for text rendering
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignCenter)
        
        # Create label if using text
        if not self.image_url:
            self.text_label = QLabel(self.text[:2].upper())  # Use first two characters
            self.text_label.setAlignment(Qt.AlignCenter)
            font = QFont()
            font.setBold(True)
            font.setPointSize(size // 3)  # Size proportional to avatar size
            self.text_label.setFont(font)
            self.text_label.setStyleSheet("color: white; background: transparent;")
            self.layout.addWidget(self.text_label)
    
    def load_image_from_url(self):
        """Load image from URL and set as avatar background"""
        try:
            # Use a network manager to download the image
            self.network_manager = QNetworkAccessManager()
            self.network_manager.finished.connect(self.on_image_downloaded)
            self.network_manager.get(QNetworkRequest(QUrl(self.image_url)))
        except Exception as e:
            print(f"Error loading image from URL: {e}")
            # Fallback to text-based avatar if URL loading fails
            self.image_url = None
    
    def on_image_downloaded(self, reply):
        """Process downloaded image and apply to the avatar"""
        try:
            if reply.error() == QNetworkReply.NoError:
                data = reply.readAll()
                pixmap = QPixmap()
                pixmap.loadFromData(data)
                
                # Create a circular mask for the image
                if not pixmap.isNull():
                    self.pixmap = self.create_circular_pixmap(pixmap)
                    self.update()  # Trigger repaint
                else:
                    self.image_url = None  # Fallback if pixmap is null
            else:
                print(f"Error downloading image: {reply.errorString()}")
                self.image_url = None  # Fallback if download failed
        except Exception as e:
            print(f"Error processing downloaded image: {e}")
            self.image_url = None
    
    def create_circular_pixmap(self, source_pixmap):
        """Create a circular version of the pixmap"""
        target = QPixmap(self.size, self.size)
        target.fill(Qt.transparent)
        
        painter = QPainter(target)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create circular path
        path = QPainterPath()
        path.addEllipse(0, 0, self.size, self.size)
        
        # Clip to circle
        painter.setClipPath(path)
        
        # Scale and center the image
        scaled_pixmap = source_pixmap.scaled(self.size, self.size, 
                                            Qt.KeepAspectRatioByExpanding, 
                                            Qt.SmoothTransformation)
        
        # Calculate position to center the image if aspect ratio is not 1:1
        x = (self.size - scaled_pixmap.width()) // 2 if scaled_pixmap.width() > self.size else 0
        y = (self.size - scaled_pixmap.height()) // 2 if scaled_pixmap.height() > self.size else 0
        
        painter.drawPixmap(x, y, scaled_pixmap)
        painter.end()
        
        return target
    
    def paintEvent(self, event):
        """Custom paint event to draw the pixmap if available"""
        super().paintEvent(event)
        
        if hasattr(self, 'pixmap') and not self.pixmap.isNull():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.drawPixmap(0, 0, self.pixmap)
            painter.end()

# Improved search bar

# Responsive header with improved styling
class Header(QFrame):
    def __init__(self, parent=None, user=None):
        super().__init__(parent)

        self.user_name = user.get('username', 'User')
        self.profile_pic_url = user.get('profilePicture', None)

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


        title_layout.addWidget(title)


        # Actions section with notification and profile
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(15)




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
        avatar_content = self.profile_pic_url if self.profile_pic_url else self.user_name
        avatar = AvatarWidget(avatar_content, size=36)
        avatar_layout = QVBoxLayout(profile_btn)
        avatar_layout.setContentsMargins(0, 0, 0, 0)
        avatar_layout.setAlignment(Qt.AlignCenter)
        avatar_layout.addWidget(avatar)

        actions_layout.addWidget(profile_btn)

        # Add all elements to main layout - responsive arrangement
        layout.addLayout(title_layout)
        layout.addStretch(1)  # Push search to center
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

        # Icon based on stock initials
        stocks_initials = "".join([word[0] for word in transaction_data["name"].split()])

        icon_text = "B" if transaction_data["type"] == "buy" else "S"
        # Random color from palette
        random_color = random.choice(ColorPalette.CHART_COLORS)
        icon = AvatarWidget(stocks_initials, size=40, background_color=random_color)

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
    def __init__(self, parent=None, user=None, user_stocks=None, user_transactions=None, stocks_the_user_has=None, firebaseUserId=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)



        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        self.user = user
        self.user_stocks = user_stocks
        self.user_transactions = user_transactions
        self.stocks_the_user_has = stocks_the_user_has
        self.firebaseUserId = firebaseUserId


        user_name = self.user.get('username', 'User').split()[0] if self.user else 'User'

        # Header with welcome message
        header = Header(user=user)
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

        # Create the portfolio card with actual data
        self.portfolio_card = PortfolioSummaryCard(
            user_stocks=self.user_stocks,
            stocks_data=self.stocks_the_user_has
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

    def convert_transaction_data(self, api_transactions):
        """Convert API transaction format to UI format"""
        import datetime
        
        ui_transactions = []
        for tx in api_transactions:
            try:
                # Parse date - Fix for handling the specific format
                date_str = tx['date']
                
                # Handle microseconds properly by making sure it has exactly 6 digits
                if '.' in date_str:
                    base, ms_part = date_str.split('.')
                    # Remove any trailing 'Z' or timezone info first
                    ms_part = ms_part.rstrip('Z').split('+')[0].split('-')[0]
                    # Pad or truncate microseconds to exactly 6 digits
                    ms_part = ms_part.ljust(6, '0')[:6]
                    date_str = f"{base}.{ms_part}"
                
                # Use strptime instead of fromisoformat for more flexible parsing
                tx_date = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
                formatted_date = tx_date.strftime("%b %d, %Y")
                
                # Get full name if available
                symbol = tx['stockSymbol']
                name = symbol
                if hasattr(self, 'stocks_the_user_has') and self.stocks_the_user_has and symbol in self.stocks_the_user_has:
                    name = self.stocks_the_user_has[symbol].get('name', symbol)
                
                ui_transactions.append({
                    "name": name,
                    "type": tx['transactionType'].lower(),
                    "date": formatted_date,
                    "price": f"{tx['price']:.2f}",
                    "shares": str(tx['quantity'])
                })
            except Exception as e:
                print(f"Error processing transaction: {e}")
                print(f"Transaction data: {tx}")
        
        return ui_transactions

    def convert_stock_data(self, user_stocks, stocks_details):
        """Convert API stock format to UI format with aggregated quantities"""
        from collections import defaultdict
        
        stock_quantities = defaultdict(int)
        for stock in user_stocks:
            symbol = stock['stockSymbol']
            stock_quantities[symbol] += stock['quantity']
        
        ui_stocks = []
        for symbol, total_quantity in stock_quantities.items():
            if symbol in stocks_details:
                details = stocks_details[symbol]
                
                ui_stocks.append({
                    "name": details['name'],
                    "amount": str(total_quantity),  # Total quantity across all transactions
                    "price": f"{details['currentPrice']:.2f}",
                    "change": details['changePercent']
                })
        
        return ui_stocks

    def _setup_portfolio_details_section(self):
        """Setup the portfolio details section with owned stocks and recent activity"""
        section = QWidget()
        section_layout = QHBoxLayout(section)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(20)

        # Owned stocks widget - reduced size
        ui_stocks = self.convert_stock_data(self.user_stocks, self.stocks_the_user_has)
        self.owned_stocks = OwnedStocksWidget(stocks=ui_stocks, stocks_the_user_has=self.stocks_the_user_has)
        self.owned_stocks.setMinimumHeight(350)
        

        # Recent activity card
        self.recent_activity = Card("Recent Activity")

        recent_layout = QVBoxLayout()
        recent_layout.setContentsMargins(20, 20, 20, 20)
        recent_layout.setSpacing(10)

        # Create transaction items
        transaction_container = QWidget()
        transaction_layout = QVBoxLayout(transaction_container)
        transaction_layout.setContentsMargins(0, 0, 0, 0)
        transaction_layout.setSpacing(0)

        if not self.user_transactions:
            # Show empty state
            empty_label = QLabel("No recent transactions")
            empty_label.setStyleSheet(f"""
                color: {ColorPalette.TEXT_SECONDARY};
                font-size: 14px;
                text-align: center;
                padding: 30px;
            """)
            empty_label.setAlignment(Qt.AlignCenter)
            transaction_layout.addWidget(empty_label)
        else:
            # Show actual transactions (limited to most recent 3)
            # Get 4 latest transactions
            recent_transactions = self.user_transactions[-4:]
            
            # Convert all transactions at once
            ui_transactions = self.convert_transaction_data(recent_transactions)
            
            for i, tx_data in enumerate(ui_transactions):
                item = TransactionItem(tx_data, is_last=(i == len(ui_transactions) - 1))
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

        self.view_all_btn = view_all_btn

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

    def update_dashboard_data(self, user_stocks=None, user_transactions=None, stocks_the_user_has=None):
        """Update dashboard with new data without recreating the entire UI"""
        # Update stored data
        if user_stocks is not None:
            self.user_stocks = user_stocks
        if user_transactions is not None:
            self.user_transactions = user_transactions
        if stocks_the_user_has is not None:
            self.stocks_the_user_has = stocks_the_user_has
        
        # Update portfolio card
        if hasattr(self, 'portfolio_card'):
            self.portfolio_card.update_data(
                user_stocks=self.user_stocks,
                stocks_data=self.stocks_the_user_has
            )
        
        # Update owned stocks widget
        if hasattr(self, 'owned_stocks'):
            # Convert data to UI format
            ui_stocks = self.convert_stock_data(self.user_stocks, self.stocks_the_user_has)
            self._update_owned_stocks_widget(ui_stocks)
        
        # Update recent transactions
        if hasattr(self, 'recent_activity'):
            self._update_recent_transactions()

        
    
    def _update_owned_stocks_widget(self, ui_stocks):
        """Update the existing OwnedStocksWidget with new stocks"""
        if not hasattr(self, 'owned_stocks'):
            print("Warning: owned_stocks widget not found")
            return
        
        # Find the stocks container within the OwnedStocksWidget
        stocks_scroll = self.owned_stocks.findChild(QScrollArea)
        if not stocks_scroll:
            print("Warning: Could not find stocks scroll area")
            return
        
        stocks_container = stocks_scroll.widget()
        if not stocks_container:
            print("Warning: Could not find stocks container")
            return
        
        stocks_layout = stocks_container.layout()
        if not stocks_layout:
            print("Warning: Stocks container has no layout")
            return
        
        # Clear existing stock items
        for i in reversed(range(stocks_layout.count())):
            widget = stocks_layout.itemAt(i).widget()
            if isinstance(widget, StockItem):
                stocks_layout.removeWidget(widget)
                widget.deleteLater()
        
        # Add new stock items
        if not ui_stocks:
            # Show empty state
            empty_label = QLabel("You don't have any stocks yet")
            empty_label.setStyleSheet(f"""
                color: {ColorPalette.TEXT_SECONDARY};
                font-size: 14px;
                text-align: center;
                padding: 30px;
            """)
            empty_label.setAlignment(Qt.AlignCenter)
            stocks_layout.addWidget(empty_label)
        else:
            # Show actual stocks
            for i, stock in enumerate(ui_stocks):
                item = StockItem(stock, is_last=(i == len(ui_stocks) - 1))
                stocks_layout.addWidget(item)
        
        # Add spacer to push items to top
        stocks_layout.addStretch(1)
    
    def _update_recent_transactions(self):
        """Update the recent transactions widget with new data"""
        
        # Find the transaction container within the recent activity card
        transaction_scroll = self.recent_activity.findChild(QScrollArea)
        
        if not transaction_scroll:
            print("Warning: Could not find scroll area in recent activity")
            return
        
        transaction_container = transaction_scroll.widget()
        if not transaction_container:
            print("Warning: Could not find transaction container")
            return
        
        # Get the layout of the transaction container
        transaction_layout = transaction_container.layout()
        if not transaction_layout:
            print("Warning: Transaction container has no layout")
            return
        
        # Clear existing items
        for i in reversed(range(transaction_layout.count())):
            widget = transaction_layout.itemAt(i).widget()
            if isinstance(widget, TransactionItem) or isinstance(widget, QLabel):
                transaction_layout.removeWidget(widget)
                widget.deleteLater()
        
        # Add new transaction items
        if not self.user_transactions:
            # Show empty state
            empty_label = QLabel("No recent transactions")
            empty_label.setStyleSheet(f"""
                color: {ColorPalette.TEXT_SECONDARY};
                font-size: 14px;
                text-align: center;
                padding: 30px;
            """)
            empty_label.setAlignment(Qt.AlignCenter)
            transaction_layout.addWidget(empty_label)
        else:
            # Show actual transactions (limited to most recent 4)
            recent_transactions = self.user_transactions[-4:]
            
            # Convert all transactions at once
            ui_transactions = self.convert_transaction_data(recent_transactions)
            
            for i, tx_data in enumerate(ui_transactions):
                item = TransactionItem(tx_data, is_last=(i == len(ui_transactions) - 1))
                transaction_layout.addWidget(item)
        
        # Add spacer to push transactions to the top if fewer than max
        transaction_layout.addStretch(1)


# Responsive main application window
class MainWindow(QWidget):
    def __init__(self, user=None, user_stocks=None, user_transactions=None, firebaseUserId=None, balance=None, stocks_the_user_has=None):
        super().__init__()
        self.setWindowTitle("StockMaster Pro")
        self.setMinimumSize(900, 650)  # Reduced minimum size
        print("user" + str(user))
        print("user_stocks" + str(user_stocks))
        print("user_transactions" + str(user_transactions))
        print("User balance" + str(balance))


        
        self.user = user
        self.user_stocks = user_stocks
        self.user_transactions = user_transactions
        self.firebaseUserId = firebaseUserId
        self.balance = balance
        self.stocks_the_user_has = stocks_the_user_has
        print("Stocks the user has: ", self.stocks_the_user_has)


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
        self.sidebar = Sidebar(user=self.user)
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

        self.dashboard = DashboardPage(
            user=self.user, 
            user_stocks=self.user_stocks, 
            user_transactions=self.user_transactions, 
            stocks_the_user_has=self.stocks_the_user_has,
            firebaseUserId=self.firebaseUserId
        )

        # Create model and presenter for dashboard
        from Model.Dashboard.dashboard_model import DashboardModel
        from Presenter.Dashboard.dashboard_presenter import DashboardPresenter

        dashboard_model = DashboardModel()
        self.dashboard_presenter = DashboardPresenter(self.dashboard, dashboard_model)

        # Load initial data through the presenter
        self.dashboard_presenter.load_initial_data()

        self._connect_ai_advisor_buttons()
        self._connect_add_stock_buttons()
        self._connect_view_all_transactions()
        self._connect_view_all_stocks()



        # Add to layout
        self.content_layout.addWidget(self.dashboard)

        self.main_layout.addWidget(self.content_area)


        # Connect to resize event to handle responsive layouts
        self.installEventFilter(self)
        self._adjust_responsive_layout()

        from event_system import event_system
        
        # Connect to the signal with a debug print to confirm it's connecting
        print("Connecting MainWindow to data_updated signal")
        event_system.data_updated.connect(self.update_values)
        print("Connection established")


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


    def update_values(self, user_stocks=None, user_transactions=None, stocks_the_user_has=None):
        """Update the stored data across the main window and dashboard"""
        print("MainWindow received data update signal")
        
        if user_stocks is not None:
            self.user_stocks = user_stocks
        if user_transactions is not None:
            self.user_transactions = user_transactions
        if stocks_the_user_has is not None:
            self.stocks_the_user_has = stocks_the_user_has
            
        # Update dashboard if it exists
        if hasattr(self, 'dashboard') and self.dashboard:
            self.dashboard.update_dashboard_data(
                user_stocks=self.user_stocks,
                user_transactions=self.user_transactions,
                stocks_the_user_has=self.stocks_the_user_has
            )

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

    def create_stock_search_window(self):
        """Create and connect stock search components"""
        from Model.Stocks.stocks_model import StocksModel
        from View.stock_search_window import StockSearchWindow
        from Presenter.Stocks.stocks_presenter import StocksPresenter
        
        # Create components
        model = StocksModel()
        print("firebaseUserId" + str(self.firebaseUserId))
        f = self.firebaseUserId
        view = StockSearchWindow(str(f))
        
        # Create presenter and pass view and model
        # The presenter connects to UI elements in its constructor
        presenter = StocksPresenter(view, model)

        view.presenter = presenter
        
        return view
    
    def create_profile_page(self):
        from View.profile_page import ProfilePage
        from Model.Profile.profile_model import ProfileModel
        from Presenter.Profile.profile_presenter import ProfilePresenter

        model = ProfileModel()

        view = ProfilePage(self.user, self.balance, self.firebaseUserId)
        presenter = ProfilePresenter(view, model)
        view.presenter = presenter
        return view
    

    def create_protofilio_page(self, user, user_stocks, stocks_the_user_has, balance, firebaseUserId):
        from View.protofilio_view import PortfolioPage
        from Model.Protofilio.protofilio_model import PortfolioModel
        from Presenter.Protofilio.protofilio_presenter import PortfolioPresenter

        model = PortfolioModel()
        view = PortfolioPage(user, user_stocks, stocks_the_user_has, balance, firebaseUserId)
        presenter = PortfolioPresenter(view, model)
        view.presenter = presenter
        return view

    def _connect_sidebar_buttons(self):
        """Connect sidebar buttons to their actions"""
        # AI Advisor button - opens a separate window
        self.sidebar.ai_chat.clicked.connect(self._open_ai_advisor)
        self.sidebar.portfolio_btn.clicked.connect(self._open_portfolio)
        self.sidebar.transactions_btn.clicked.connect(self._open_transactions)
        self.sidebar.profile_btn.clicked.connect(self._open_profile)
        self.sidebar.all_stocks.clicked.connect(self._open_stock_page)

    def _connect_ai_advisor_buttons(self):
        self.dashboard.ai_advice.view_button.clicked.connect(self._open_ai_advisor)

    def _connect_add_stock_buttons(self):
        self.dashboard.owned_stocks.add_btn.clicked.connect(self._open_stock_page)

    def _connect_view_all_stocks(self):
        self.dashboard.owned_stocks.view_all_btn.clicked.connect(self._open_portfolio)

    def _connect_view_all_transactions(self):
        self.dashboard.view_all_btn.clicked.connect(self._open_transactions)

    def _open_stock_page(self):
        print("Open stock page")
        """Open a stock page for the selected stock"""
        # Store a reference to prevent garbage collection
        stock_window = self.create_stock_search_window()
        stock_window.show()
        
        # Store reference to prevent garbage collection
        self.stock_window = stock_window
        
    def _open_ai_advisor(self):
        """Open the AI Advisor window"""
        # Store a reference to prevent garbage collection
        self.ai_window = AIAdvisorWindow()
        self.ai_window.show()

    def _open_portfolio(self):
        """Open the Portfolio window with real data"""
        # Store a reference to prevent garbage collection
        portfolio_window = self.create_protofilio_page(
            user=self.user, 
            user_stocks=self.user_stocks, 
            stocks_the_user_has=self.stocks_the_user_has,
            balance=self.balance,
            firebaseUserId=self.firebaseUserId
        )
        portfolio_window.show()
        self.portfolio_window = portfolio_window


    def _open_transactions(self):
        
        """Open the Transactions window"""
        # Store a reference to prevent garbage collection
        self.transactions_window = TransactionsPage(
            user=self.user, 
            user_transactions=self.user_transactions, 
            stocks_the_user_has=self.stocks_the_user_has,
            balance=self.balance
        )
        self.transactions_window.show()

    
    def _open_profile(self):
        """Open the Profile window"""
        profile_window = self.create_profile_page()
        profile_window.show()
        self.profile_window = profile_window


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())