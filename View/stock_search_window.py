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
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QSpinBox, QDoubleSpinBox, 
                             QFormLayout, QDialogButtonBox, QMessageBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor


class PurchaseDialog(QDialog):
    """Dialog for purchasing stocks"""
    
    # Signal emitted when purchase is confirmed
    purchase_confirmed = Signal(str, float, float)  # symbol, quantity, price
    
    def __init__(self, stock_data, parent=None):
        super().__init__(parent)
        self.stock_data = stock_data
        
        # Set window properties
        self.setWindowTitle(f"Buy {stock_data['symbol']} Stock")
        self.setMinimumWidth(400)
        self.setModal(True)
        
        # Apply styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {ColorPalette.BG_DARK};
                color: {ColorPalette.TEXT_PRIMARY};
                font-family: 'Segoe UI', Arial, sans-serif;
                border-radius: 8px;
            }}
        """)


        # Create layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(20)
        
        # Header with stock information
        self._setup_header()
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"background-color: {ColorPalette.BORDER_DARK}; margin: 5px 0;")
        separator.setFixedHeight(1)
        self.main_layout.addWidget(separator)
        
        # Purchase form
        self._setup_purchase_form()
        
        # Order summary
        self._setup_order_summary()
        
        # Action buttons
        self._setup_action_buttons()
        
        # Connect signals and slots
        self._connect_signals()
    
    def _setup_header(self):
        """Setup the dialog header with stock information"""
        header_layout = QHBoxLayout()
        
        # Stock name and symbol
        stock_info_layout = QVBoxLayout()
        
        symbol_label = QLabel(self.stock_data["symbol"])
        symbol_label.setStyleSheet(f"""
            color: {ColorPalette.TEXT_PRIMARY};
            font-size: 22px;
            font-weight: bold;
        """)
        
        name_label = QLabel(self.stock_data["name"])
        name_label.setStyleSheet(f"""
            color: {ColorPalette.TEXT_SECONDARY};
            font-size: 14px;
        """)
        
        stock_info_layout.addWidget(symbol_label)
        stock_info_layout.addWidget(name_label)
        
        # Current price
        price_layout = QVBoxLayout()
        price_layout.setAlignment(Qt.AlignRight)
        
        current_price_label = QLabel(f"${self.stock_data['price']}")
        current_price_label.setStyleSheet(f"""
            color: {ColorPalette.TEXT_PRIMARY};
            font-size: 22px;
            font-weight: bold;
        """)
        
        price_label = QLabel("Current Price")
        price_label.setStyleSheet(f"""
            color: {ColorPalette.TEXT_SECONDARY};
            font-size: 12px;
        """)
        
        price_layout.addWidget(current_price_label)
        price_layout.addWidget(price_label)
        
        # Add to header layout
        header_layout.addLayout(stock_info_layout)
        header_layout.addStretch()
        header_layout.addLayout(price_layout)
        
        self.main_layout.addLayout(header_layout)
    
    def _setup_purchase_form(self):
        """Setup the form for specifying purchase details"""
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft)
        
        # Quantity input
        quantity_label = QLabel("Quantity:")
        quantity_label.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-size: 14px;")
        
        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(1)
        self.quantity_input.setMaximum(10000)
        self.quantity_input.setValue(1)
        self.quantity_input.setFixedHeight(40)
        self.quantity_input.setStyleSheet(f"""
            QSpinBox {{
                background-color: {ColorPalette.BG_CARD};
                color: {ColorPalette.TEXT_PRIMARY};
                border: 1px solid {ColorPalette.BORDER_DARK};
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background-color: {ColorPalette.BORDER_LIGHT};
                border-radius: 3px;
                width: 16px;
                height: 12px;
            }}
        """)
        
        # Order type (Market, Limit, etc) - simplified for now
        order_type_label = QLabel("Order Type:")
        order_type_label.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-size: 14px;")
        
        self.order_type = QLabel("Market Order")
        self.order_type.setStyleSheet(f"""
            color: {ColorPalette.TEXT_PRIMARY};
            font-size: 14px;
            background-color: {ColorPalette.BG_CARD};
            border: 1px solid {ColorPalette.BORDER_DARK};
            border-radius: 6px;
            padding: 10px;
        """)
        
        # Add to form layout
        form_layout.addRow(quantity_label, self.quantity_input)
        form_layout.addRow(order_type_label, self.order_type)
        
        self.main_layout.addLayout(form_layout)
    
    def _setup_order_summary(self):
        """Setup the order summary section"""
        # Container for order summary
        summary_frame = QFrame()
        summary_frame.setStyleSheet(f"""
            background-color: {ColorPalette.BG_CARD};
            border-radius: 6px;
            padding: 10px;
        """)
        
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setContentsMargins(15, 15, 15, 15)
        summary_layout.setSpacing(10)
        
        # Summary title
        summary_title = QLabel("Order Summary")
        summary_title.setStyleSheet(f"""
            color: {ColorPalette.TEXT_PRIMARY};
            font-size: 16px;
            font-weight: bold;
        """)
        summary_layout.addWidget(summary_title)
        
        # Summary details
        details_layout = QFormLayout()
        details_layout.setSpacing(8)
        details_layout.setLabelAlignment(Qt.AlignLeft)
        details_layout.setFormAlignment(Qt.AlignRight)
        
        # Stock price
        price_label = QLabel("Price per Share:")
        price_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 14px;")
        
        self.price_value = QLabel(f"${self.stock_data['price']}")
        self.price_value.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-size: 14px;")
        
        # Estimated cost
        cost_label = QLabel("Estimated Cost:")
        cost_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 14px;")
        
        self.cost_value = QLabel(f"${self.stock_data['price']}")  # Initial value for 1 share
        self.cost_value.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-size: 14px; font-weight: bold;")
        
        # Commission (simplified)
        commission_label = QLabel("Commission:")
        commission_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 14px;")
        
        self.commission_value = QLabel("$0.00")  # Assuming no commission for simplicity
        self.commission_value.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-size: 14px;")
        
        # Total
        total_label = QLabel("Total:")
        total_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 14px; font-weight: bold;")
        
        self.total_value = QLabel(f"${self.stock_data['price']}")  # Initial value for 1 share
        self.total_value.setStyleSheet(f"color: {ColorPalette.ACCENT_PRIMARY}; font-size: 16px; font-weight: bold;")
        
        # Add to details layout
        details_layout.addRow(price_label, self.price_value)
        details_layout.addRow(cost_label, self.cost_value)
        details_layout.addRow(commission_label, self.commission_value)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"background-color: {ColorPalette.BORDER_DARK};")
        separator.setFixedHeight(1)
        
        # Add to summary layout
        summary_layout.addLayout(details_layout)
        summary_layout.addWidget(separator)
        
        # Add total
        total_layout = QHBoxLayout()
        total_layout.addWidget(total_label)
        total_layout.addStretch()
        total_layout.addWidget(self.total_value)
        
        summary_layout.addLayout(total_layout)
        
        # Add to main layout
        self.main_layout.addWidget(summary_frame)
    
    def _setup_action_buttons(self):
        """Setup the action buttons"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet(GlobalStyle.SECONDARY_BUTTON)
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.setFixedHeight(40)
        
        # Confirm Purchase button
        self.confirm_btn = QPushButton("Confirm Purchase")
        self.confirm_btn.setStyleSheet(GlobalStyle.PRIMARY_BUTTON)
        self.confirm_btn.setCursor(Qt.PointingHandCursor)
        self.confirm_btn.setFixedHeight(40)
        
        # Add to layout
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.confirm_btn)
        
        self.main_layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Connect signals to slots"""
        # Update order summary when quantity changes
        self.quantity_input.valueChanged.connect(self._update_order_summary)
        
        # Connect button actions
        self.cancel_btn.clicked.connect(self.reject)
        self.confirm_btn.clicked.connect(self._confirm_purchase)
    
    def _update_order_summary(self):
        """Update the order summary based on current input values"""
        quantity = self.quantity_input.value()
        price = self.stock_data["price"]
        
        # Calculate costs
        subtotal = quantity * price
        commission = 0.0  # Assuming no commission for simplicity
        total = subtotal + commission
        
        # Update labels
        self.cost_value.setText(f"${subtotal:.2f}")
        self.total_value.setText(f"${total:.2f}")
    
    def _confirm_purchase(self):
        """Handle purchase confirmation"""
        quantity = self.quantity_input.value()
        price = self.stock_data["price"]
        symbol = self.stock_data["symbol"]
        
        # Show confirmation dialog
        total_cost = quantity * price
        confirm_msg = QMessageBox()
        confirm_msg.setWindowTitle("Confirm Purchase")
        confirm_msg.setText(f"Are you sure you want to purchase {quantity} shares of {symbol} for ${total_cost:.2f}?")
        confirm_msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirm_msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {ColorPalette.BG_DARK};
                color: {ColorPalette.TEXT_PRIMARY};
            }}
            QMessageBox QPushButton {{
                background-color: {ColorPalette.BG_CARD};
                color: {ColorPalette.TEXT_PRIMARY};
                border: 1px solid {ColorPalette.BORDER_DARK};
                border-radius: 4px;
                padding: 5px 15px;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {ColorPalette.BORDER_LIGHT};
            }}
        """)
        
        # If confirmed, emit signal and close dialog
        if confirm_msg.exec_() == QMessageBox.Yes:
            self.purchase_confirmed.emit(symbol, quantity, price)
            self.accept()
            
            # Show success message
            success_msg = QMessageBox()
            success_msg.setWindowTitle("Purchase Successful")
            success_msg.setText(f"You have successfully purchased {quantity} shares of {symbol} for ${total_cost:.2f}.")
            success_msg.setStyleSheet(f"""
                QMessageBox {{
                    background-color: {ColorPalette.BG_DARK};
                    color: {ColorPalette.TEXT_PRIMARY};
                }}
                QMessageBox QPushButton {{
                    background-color: {ColorPalette.BG_CARD};
                    color: {ColorPalette.TEXT_PRIMARY};
                    border: 1px solid {ColorPalette.BORDER_DARK};
                    border-radius: 4px;
                    padding: 5px 15px;
                    min-width: 80px;
                }}
                QMessageBox QPushButton:hover {{
                    background-color: {ColorPalette.BORDER_LIGHT};
                }}
            """)
            success_msg.exec_()

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
    # Signal for purchase completed - if needed at card level
    purchase_completed = Signal(str, float, float)  # symbol, quantity, price
    dialog_created = Signal(object)  # Passes the dialog object
    
    def __init__(self, stock_data, parent=None):
        super().__init__(title="", parent=parent)
        self.stock_data = stock_data
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(15)

        self.purchase_dialog = None
        
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
        self.watchlist_btn = QPushButton("+ Add to Watchlist")
        self.watchlist_btn.setStyleSheet(GlobalStyle.SECONDARY_BUTTON)
        self.watchlist_btn.setCursor(Qt.PointingHandCursor)
        self.watchlist_btn.setFixedHeight(40)
        
        # Buy button
        self.buy_btn = QPushButton("Buy")
        self.buy_btn.setStyleSheet(GlobalStyle.PRIMARY_BUTTON)
        self.buy_btn.setCursor(Qt.PointingHandCursor)
        self.buy_btn.setFixedHeight(40)
        
        # Sell button
        self.sell_btn = QPushButton("Sell")
        self.sell_btn.setStyleSheet(f"""
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
        self.sell_btn.setCursor(Qt.PointingHandCursor)
        self.sell_btn.setFixedHeight(40)
        
        button_layout.addWidget(self.watchlist_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.sell_btn)
        button_layout.addWidget(self.buy_btn)
        
        main_layout.addLayout(button_layout)
        
        # Set the layout
        self.layout.addLayout(main_layout)
        
        # Connect button signals
        self.buy_btn.clicked.connect(self._show_purchase_dialog)
        self.sell_btn.clicked.connect(self._show_sell_dialog)
        self.watchlist_btn.clicked.connect(self._add_to_watchlist)
    
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
    
    def _show_purchase_dialog(self):
        """Show the purchase dialog when Buy button is clicked"""
        # Create and show the purchase dialog
        self.purchase_dialog = PurchaseDialog(self.stock_data, self.window())
        
        # Connect the purchase_confirmed signal
        self.purchase_dialog.purchase_confirmed.connect(self._handle_purchase)
        
        # Emit our new signal - the presenter can connect to this
        self.dialog_created.emit(self.purchase_dialog)
        
        # Show the dialog (modal)
        self.purchase_dialog.exec_()

    def get_confirm_button(self):
        """Get the confirm button directly from the stored dialog"""
        if self.purchase_dialog:
            return self.purchase_dialog.confirm_btn
        return None

    def _show_sell_dialog(self):
        """Show the sell dialog when Sell button is clicked"""
        # This would be similar to the purchase dialog, but for selling
        # For now, just show a message
        QMessageBox.information(
            self.window(),
            "Sell Stocks",
            f"Sell functionality for {self.stock_data['symbol']} is not implemented yet."
        )
    
    def _add_to_watchlist(self):
        """Add the stock to watchlist when button is clicked"""
        # For now, just show a message
        QMessageBox.information(
            self.window(),
            "Watchlist",
            f"{self.stock_data['symbol']} has been added to your watchlist."
        )
    
    def _handle_purchase(self, symbol, quantity, price):
        """Handle the purchase confirmation from the dialog"""
        # In a real application, this would update a portfolio model or database
        # For now, we'll just re-emit the signal for any parent to handle
        total_cost = quantity * price
        
        # Log the purchase (for demonstration)
        print(f"Purchase completed: {quantity} shares of {symbol} at ${price:.2f} for a total of ${total_cost:.2f}")
        
        # Emit the signal for any parent components to handle
        if hasattr(self, 'purchase_completed'):
            self.purchase_completed.emit(symbol, quantity, price)

class StockSearchWindow(QWidget):
    def __init__(self, firebaseId=None, parent=None):
        super().__init__(parent)
        print("StockSearchWindow")
        self.setWindowTitle("Stock Search")
        self.setMinimumSize(800, 600)
        print("User ID: ", firebaseId)
        self.firebaseId = firebaseId
        
        
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

        self.stock_card = None
        
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
        self._clear_results()
        for stock in results:
            self.stock_card = StockInfoCard(stock)
            self.content_layout.addWidget(self.stock_card)
        
        # Add spacer at the end for better layout
        self.content_layout.addStretch()

    def get_buy_button(self):
        """Get the buy button directly from the stored stock card"""
        if self.stock_card:
            return self.stock_card.buy_btn
        return None


# For testing in isolation
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StockSearchWindow()
    window.show()
    sys.exit(app.exec())