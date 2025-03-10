import sys
import os
from datetime import datetime, timedelta
import random

from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QFrame, QHBoxLayout,
                              QLabel, QLineEdit, QScrollArea, QSizePolicy, QGraphicsDropShadowEffect,
                              QTableWidget, QTableWidgetItem, QHeaderView, QSpacerItem, QComboBox)
from PySide6.QtGui import (QColor, QIcon, QPixmap, QPainter, QLinearGradient, QBrush, QPen,
                          QFont, QPainterPath, QCursor)
from PySide6.QtCore import (Qt, QSize, QRect, QTimer, QPointF, QEvent, QPoint,
                           QPropertyAnimation, Signal, QUrl, QMargins)
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

# Import shared components - adjust these imports based on your project structure
from View.shared_components import ColorPalette, GlobalStyle, AvatarWidget


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


class SearchBar(QLineEdit):
    def __init__(self, parent=None, placeholder="Search stocks..."):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet(GlobalStyle.INPUT_STYLE)
        self.setFixedHeight(40)
        self.setMinimumWidth(300)

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


class StockInfoCard(Card):
    def __init__(self, stock_data, parent=None):
        super().__init__(title="", parent=parent)
        self.stock_data = stock_data
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(15)
        
        # Header with stock name and symbol
        header_layout = QHBoxLayout()
        
        # Logo/Avatar with random color from ColorPalette.CHART_COLORS
        random_color = self._get_random_color()
        stock_avatar = AvatarWidget(self.stock_data["symbol"], size=50, background_color=random_color)
        
        # Name and symbol
        name_layout = QVBoxLayout()
        
        stock_name = QLabel(self.stock_data["name"])
        stock_name.setStyleSheet(f"""
            color: {ColorPalette.TEXT_PRIMARY};
            font-size: 20px;
            font-weight: bold;
        """)
        
        stock_symbol = QLabel(self.stock_data["symbol"])
        stock_symbol.setStyleSheet(f"""
            color: {ColorPalette.TEXT_SECONDARY};
            font-size: 14px;
        """)
        
        name_layout.addWidget(stock_name)
        name_layout.addWidget(stock_symbol)
        
        # Current price
        price_layout = QVBoxLayout()
        price_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        current_price = QLabel(f"${self.stock_data['price']}")
        current_price.setStyleSheet(f"""
            color: {ColorPalette.TEXT_PRIMARY};
            font-size: 24px;
            font-weight: bold;
        """)
        
        # Change amount
        change_value = self.stock_data["change"]
        change_color = ColorPalette.ACCENT_SUCCESS if change_value > 0 else ColorPalette.ACCENT_DANGER
        change_text = f"+{change_value}%" if change_value > 0 else f"{change_value}%"
        
        change_label = QLabel(change_text)
        change_label.setStyleSheet(f"""
            color: {change_color}; 
            font-weight: bold; 
            font-size: 16px;
            background-color: {change_color}15; 
            padding: 4px 8px; 
            border-radius: 4px;
        """)
        
        price_layout.addWidget(current_price)
        price_layout.addWidget(change_label)
        price_layout.setAlignment(change_label, Qt.AlignRight)
        
        # Add elements to header
        header_layout.addWidget(stock_avatar)
        header_layout.addLayout(name_layout)
        header_layout.addStretch()
        header_layout.addLayout(price_layout)
        
        main_layout.addLayout(header_layout)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"background-color: {ColorPalette.BORDER_DARK};")
        separator.setFixedHeight(1)
        main_layout.addWidget(separator)
        
        # Key statistics grid
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        # Left column
        left_stats = QVBoxLayout()
        self._add_stat_item(left_stats, "Open", f"${self.stock_data['open']}")
        self._add_stat_item(left_stats, "Previous Close", f"${self.stock_data['prevClose']}")
        
        # Fix for volume formatting - check if volume is already a string
        volume_value = self.stock_data['volume']
        if isinstance(volume_value, str):
            # Volume is already formatted as a string
            volume_display = volume_value
        else:
            # Format the volume as a number with commas
            volume_display = f"{volume_value:,}"
        self._add_stat_item(left_stats, "Volume", volume_display)
        
        # Middle column
        middle_stats = QVBoxLayout()
        self._add_stat_item(middle_stats, "Day's Range", f"${self.stock_data['dayLow']} - ${self.stock_data['dayHigh']}")
        self._add_stat_item(middle_stats, "52 Week Range", f"${self.stock_data['yearLow']} - ${self.stock_data['yearHigh']}")
        self._add_stat_item(middle_stats, "Market Cap", self.stock_data['marketCap'])
        
        # Right column
        right_stats = QVBoxLayout()
        self._add_stat_item(right_stats, "P/E Ratio", f"{self.stock_data['pe']}")
        self._add_stat_item(right_stats, "EPS", f"${self.stock_data['eps']}")
        self._add_stat_item(right_stats, "Dividend Yield", f"{self.stock_data['dividend']}%")
        
        stats_layout.addLayout(left_stats)
        stats_layout.addLayout(middle_stats)
        stats_layout.addLayout(right_stats)
        
        main_layout.addLayout(stats_layout)
        
        # Add buy/sell buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        # Add to watchlist button
        watchlist_btn = QPushButton("+ Add to Watchlist")
        watchlist_btn.setStyleSheet(GlobalStyle.SECONDARY_BUTTON)
        watchlist_btn.setCursor(Qt.PointingHandCursor)
        watchlist_btn.setFixedHeight(40)
        
        # Buy button
        buy_btn = QPushButton("Buy")
        buy_btn.setStyleSheet(GlobalStyle.PRIMARY_BUTTON)
        buy_btn.setCursor(Qt.PointingHandCursor)
        buy_btn.setFixedHeight(40)
        
        # Sell button
        sell_btn = QPushButton("Sell")
        sell_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ColorPalette.ACCENT_DANGER};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #E57373;
            }}
            QPushButton:pressed {{
                background-color: #B71C1C;
            }}
        """)
        sell_btn.setCursor(Qt.PointingHandCursor)
        sell_btn.setFixedHeight(40)
        
        button_layout.addWidget(watchlist_btn)
        button_layout.addStretch()
        button_layout.addWidget(sell_btn)
        button_layout.addWidget(buy_btn)
        
        main_layout.addLayout(button_layout)
        
        # Set the layout
        self.layout.addLayout(main_layout)
    
    def _add_stat_item(self, layout, label_text, value_text):
        """Add a statistic item to the given layout"""
        container = QWidget()
        item_layout = QVBoxLayout(container)
        item_layout.setContentsMargins(0, 8, 0, 8)
        item_layout.setSpacing(4)
        
        label = QLabel(label_text)
        label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
        
        value = QLabel(value_text)
        value.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-size: 15px; font-weight: bold;")
        
        item_layout.addWidget(label)
        item_layout.addWidget(value)
        
        layout.addWidget(container)
        return container
    
    def _get_random_color(self):
        """Get a random color from the ColorPalette.CHART_COLORS list"""
        if hasattr(ColorPalette, 'CHART_COLORS') and ColorPalette.CHART_COLORS:
            return random.choice(ColorPalette.CHART_COLORS)
        else:
            # Fallback colors if CHART_COLORS is not available
            fallback_colors = [
                "#4285F4",  # Blue
                "#EA4335",  # Red
                "#FBBC05",  # Yellow
                "#34A853",  # Green
                "#8E24AA",  # Purple
                "#00ACC1",  # Cyan
                "#FB8C00",  # Orange
                "#607D8B"   # Blue Grey
            ]
            return random.choice(fallback_colors)


class StockSearchWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        print("StockSearchWindow")
        self.setWindowTitle("Stock Search")
        self.setMinimumSize(800, 600)
        
        
        # Set dark theme with improved styling
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {ColorPalette.BG_DARK};
                color: {ColorPalette.TEXT_PRIMARY};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QScrollBar:vertical {{
                background: {ColorPalette.BG_DARK};
                width: 8px;
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
        """)
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        
        # Header with search functionality
        self._setup_header()
        
        # Content area
        self._setup_content_area()

    def get_search_button(self):
        return self.search_btn
    
    def get_search_text(self):
        return self.search_bar.text()
        

    def set_presenter(self, presenter):
        """
        Set the presenter for this view
        """
        self.presenter = presenter
    
    def _setup_header(self):
        """Setup the header with search bar and filters"""
        header_layout = QVBoxLayout()
        
        # Title
        title = QLabel("Stock Search")
        title.setStyleSheet(GlobalStyle.HEADER_STYLE)
        header_layout.addWidget(title)
        
        # Search and filter bar
        search_filter_layout = QHBoxLayout()
        search_filter_layout.setSpacing(15)
        
        # Enhanced search bar
        self.search_bar = SearchBar(placeholder="Search stocks by symbol or name...")
        self.search_bar.setMinimumWidth(400)
        
        # Market selector
        market_label = QLabel("Market:")
        market_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY};")
        
        self.market_combo = QComboBox()
        self.market_combo.addItems(["All Markets", "NYSE", "NASDAQ", "AMEX", "OTC"])
        self.market_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {ColorPalette.BG_CARD};
                color: {ColorPalette.TEXT_PRIMARY};
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                min-width: 120px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border: none;
            }}
        """)
        
        # Sector filter
        sector_label = QLabel("Sector:")
        sector_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY};")
        
        self.sector_combo = QComboBox()
        self.sector_combo.addItems(["All Sectors", "Technology", "Healthcare", "Finance", "Consumer", "Energy", "Industrial", "Utilities"])
        self.sector_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {ColorPalette.BG_CARD};
                color: {ColorPalette.TEXT_PRIMARY};
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                min-width: 120px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border: none;
            }}
        """)
        
        # Add search button
        self.search_btn = QPushButton("Search")
        self.search_btn.setStyleSheet(GlobalStyle.PRIMARY_BUTTON)
        self.search_btn.setCursor(Qt.PointingHandCursor)
        self.search_btn.setFixedHeight(40)
        self.search_btn.setMinimumWidth(100)

        
        # Add to layout
        search_filter_layout.addWidget(self.search_bar, 1)  # Give search more space
        search_filter_layout.addWidget(market_label)
        search_filter_layout.addWidget(self.market_combo)
        search_filter_layout.addWidget(sector_label)
        search_filter_layout.addWidget(self.sector_combo)
        search_filter_layout.addWidget(self.search_btn)
        
        header_layout.addLayout(search_filter_layout)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"background-color: {ColorPalette.BORDER_DARK};")
        separator.setFixedHeight(1)
        header_layout.addWidget(separator)
        
        self.main_layout.addLayout(header_layout)
    
    def _setup_content_area(self):
        """Setup the scrollable content area for search results"""
        # Scroll area for stock cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """)
        
        # Container for all stock cards
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(20)
        
        # Initial state - show a message to search
        self.initial_message = QLabel("Enter a stock symbol or name to search")
        self.initial_message.setAlignment(Qt.AlignCenter)
        self.initial_message.setStyleSheet(f"""
            color: {ColorPalette.TEXT_SECONDARY};
            font-size: 18px;
            padding: 40px;
        """)
        self.content_layout.addWidget(self.initial_message)
        
        # No results message (hidden initially)
        self.no_results_message = QLabel("No stocks found for your search criteria")
        self.no_results_message.setAlignment(Qt.AlignCenter)
        self.no_results_message.setStyleSheet(f"""
            color: {ColorPalette.TEXT_SECONDARY};
            font-size: 18px;
            padding: 40px;
        """)
        self.no_results_message.setVisible(False)
        self.content_layout.addWidget(self.no_results_message)
        
        # Set scroll area
        self.scroll_area.setWidget(self.content_widget)
        self.main_layout.addWidget(self.scroll_area)
    
    
    def _perform_search(self):
        """Perform a search based on current criteria"""
        search_text = self.search_bar.text().strip().upper()
        
        # Clear previous results
        self._clear_results()
        
        # Show no results or initial message if empty search
        if not search_text:
            self.initial_message.setVisible(True)
            self.no_results_message.setVisible(False)
            return
        
        # Filter results based on search text
        filtered_results = [
            stock for stock in self.stock_results 
            if search_text in stock["symbol"].upper() or search_text in stock["name"].upper()
        ]
        
        # Show results or no results message
        if filtered_results:
            self._show_search_results(filtered_results)
            self.initial_message.setVisible(False)
            self.no_results_message.setVisible(False)
        else:
            self.initial_message.setVisible(False)
            self.no_results_message.setVisible(True)
    
    def _clear_results(self):
        """Clear previous search results"""
        # Remove stock cards but keep the messages
        for i in reversed(range(self.content_layout.count())):
            item = self.content_layout.itemAt(i)
            if item and item.widget() and item.widget() not in [self.initial_message, self.no_results_message]:
                widget = item.widget()
                self.content_layout.removeWidget(widget)
                widget.deleteLater()
    
    def _show_search_results(self, results):
        """Display the search results"""
        for stock in results:
            stock_card = StockInfoCard(stock)
            self.content_layout.addWidget(stock_card)
        
        # Add spacer at the end for better layout
        self.content_layout.addStretch()


# For testing in isolation
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StockSearchWindow()
    window.show()
    sys.exit(app.exec())