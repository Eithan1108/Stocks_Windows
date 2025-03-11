import sys
import os
from datetime import datetime, timedelta
import random

from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QFrame, QHBoxLayout,
                               QLabel, QGridLayout, QScrollArea, QSizePolicy, QGraphicsDropShadowEffect,
                               QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QComboBox, 
                               QTabWidget, QStackedWidget, QBoxLayout, QToolButton, QMenu)
from PySide6.QtGui import (QColor, QAction, QFont, QPainter, QLinearGradient, QBrush, QPen,
                           QFontMetrics, QIcon, QPixmap, QCursor, QPainterPath)
from PySide6.QtCore import (Qt, QSize, QRect, QTimer, QEvent, QPoint, QPointF, 
                            QPropertyAnimation, Signal)

# Import shared components from previous files
from View.shared_components import ColorPalette, GlobalStyle, AvatarWidget


class TransactionsPage(QWidget):
    def __init__(self, parent=None, user=None, user_transactions=None, stocks_the_user_has=None, balance=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Store user data
        self.user = user
        self.user_transactions = user_transactions or []
        self.stocks_the_user_has = stocks_the_user_has or {}
        self.balance = balance
        
        # Set the same background color as main window
        self.setStyleSheet(f"background-color: {ColorPalette.BG_DARK};")
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Header with transaction overview
        header = self._create_header()
        layout.addWidget(header)
        
        # Scrollable content area
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
        
        # Content widget
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 0, 20, 20)
        self.content_layout.setSpacing(20)
        
        # Create transaction sections
        self._setup_transaction_history_section()
        self._setup_transaction_analysis_section()
        
        # Set the scroll area widget
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)
        
        # Generate transaction data or use provided data
        self._generate_transactions()
        
        # Install event filter for responsive design
        self.installEventFilter(self)
    
    def _create_header(self):
        """Create a header with transaction summary and key actions"""
        header = QFrame()
        header.setMinimumHeight(80)
        header.setStyleSheet("background-color: transparent;")
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)
        header_layout.setSpacing(20)
        
        # Title and subtitle - same styling as main window
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)
        
        title = QLabel("Transaction History")
        title.setStyleSheet(GlobalStyle.HEADER_STYLE)
        
        subtitle = QLabel("Track and analyze your investment activities")
        subtitle.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 14px;")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        # Transaction metrics
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(20)
        
        # Calculate metrics dynamically
        total_transactions = len(self.user_transactions)
        total_deposits = sum(1 for tx in self.user_transactions if tx['transactionType'].lower() == 'deposit')
        total_withdrawals = sum(1 for tx in self.user_transactions if tx['transactionType'].lower() == 'withdrawal')
        
        metrics = [
            {"label": "Total Transactions", "value": str(total_transactions)},
            {"label": "Buying Power", "value": f"${self.balance:,.2f}" if self.balance is not None else "N/A"},
            {"label": "Pending Orders", "value": str(total_withdrawals)}
        ]
        
        for metric in metrics:
            metric_widget = QWidget()
            metric_layout = QVBoxLayout(metric_widget)
            metric_layout.setContentsMargins(0, 0, 0, 0)
            metric_layout.setSpacing(4)
            
            label = QLabel(metric["label"])
            label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
            
            value = QLabel(metric["value"])
            value.setStyleSheet(f"""
                color: {ColorPalette.TEXT_PRIMARY}; 
                font-size: 16px; 
                font-weight: bold;
            """)
            
            metric_layout.addWidget(label)
            metric_layout.addWidget(value)
            
            metrics_layout.addWidget(metric_widget)
        
        # Action buttons - same styling as main window
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)

        # Combine layouts
        header_layout.addLayout(title_layout)
        header_layout.addStretch(1)
        header_layout.addLayout(metrics_layout)
        header_layout.addLayout(action_layout)
        
        return header

    def convert_transaction_data(self):
        """Convert raw transaction data to UI format"""
        ui_transactions = []
        
        try:
            for tx in self.user_transactions:
                # Parse date - Fix for handling the specific format
                try:
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
                    tx_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
                    formatted_date = tx_date.strftime("%b %d, %Y")
                except Exception as date_err:
                    print(f"Error parsing date: {date_err}")
                    formatted_date = tx['date']
                
                # Get full stock name if available
                symbol = tx.get('stockSymbol', '')
                name = symbol
                if symbol and self.stocks_the_user_has and symbol in self.stocks_the_user_has:
                    name = self.stocks_the_user_has[symbol].get('name', symbol)
                
                ui_transactions.append({
                    "date": formatted_date,
                    "type": tx['transactionType'].lower(),
                    "stock": symbol,
                    "shares": tx.get('quantity'),
                    "price": tx.get('price'),
                    "total": tx.get('price', 0) * tx.get('quantity', 1) if tx.get('quantity') and tx.get('price') else tx.get('amount', 0),
                    "status": "Completed"  # Assuming all transactions are completed
                })
        except Exception as e:
            print(f"Error converting transaction data: {e}")
        
        return ui_transactions
    def _generate_transactions(self):
        """Generate transaction table using converted transaction data"""
        # Convert raw transaction data to UI format
        transactions = self.convert_transaction_data()
        
        # Update table with converted transactions
        self.transaction_table.setRowCount(len(transactions))
        
        for row, transaction in enumerate(transactions):
            # Date
            date_item = QTableWidgetItem(transaction["date"])
            date_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
            # Type with colored styling
            type_item = QTableWidgetItem()
            type_item.setText(transaction["type"].capitalize())
            type_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
            # Set color based on transaction type
            if transaction["type"] == "buy":
                type_item.setForeground(QColor(ColorPalette.ACCENT_SUCCESS))
            elif transaction["type"] == "sell":
                type_item.setForeground(QColor(ColorPalette.ACCENT_DANGER))
            elif transaction["type"] == "dividend":
                type_item.setForeground(QColor(ColorPalette.ACCENT_INFO))
            elif transaction["type"] == "deposit":
                type_item.setForeground(QColor(ColorPalette.ACCENT_PRIMARY))
            
            # Stock
            stock_item = QTableWidgetItem(transaction["stock"])
            stock_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
            # Shares/Price - combined column
            shares_price_text = ""
            if transaction["shares"] is not None and transaction["price"] is not None:
                shares_price_text = f"{transaction['shares']} shares @ ${transaction['price']:.2f}"
            shares_price_item = QTableWidgetItem(shares_price_text)
            shares_price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Total with dollar sign
            total_text = f"${transaction['total']:.2f}"
            if transaction["type"] == "withdrawal":
                total_text = f"-{total_text}"  # Add negative sign for withdrawals
                
            total_item = QTableWidgetItem(total_text)
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Status
            status_item = QTableWidgetItem(transaction["status"])
            status_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
            # Style status based on value
            if transaction["status"] == "Completed":
                status_item.setForeground(QColor(ColorPalette.ACCENT_SUCCESS))
            
            # Set items in the table
            self.transaction_table.setItem(row, 0, date_item)
            self.transaction_table.setItem(row, 1, type_item)
            self.transaction_table.setItem(row, 2, stock_item)
            self.transaction_table.setItem(row, 3, shares_price_item)
            self.transaction_table.setItem(row, 4, total_item)
            self.transaction_table.setItem(row, 5, status_item)
            
            # Set row height
            self.transaction_table.setRowHeight(row, 50)

    def _setup_transaction_history_section(self):
        """Create transaction history section with table matching app style"""
        # Create card with same styling as main window
        history_card = QFrame()
        history_card.setStyleSheet(GlobalStyle.CARD_STYLE)
        
        # Shadow effect - exact match to main window
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        history_card.setGraphicsEffect(shadow)
        
        history_layout = QVBoxLayout(history_card)
        history_layout.setContentsMargins(20, 20, 20, 20)
        history_layout.setSpacing(15)
        
        # Title and search
        header_layout = QHBoxLayout()
        
        title = QLabel("Recent Transactions")
        title.setStyleSheet(GlobalStyle.SUBHEADER_STYLE)
        
        # Search box
        search_box = QLineEdit()
        search_box.setPlaceholderText("Search transactions...")
        search_box.setFixedWidth(250)
        search_box.setStyleSheet(f"""
            QLineEdit {{
                background-color: {ColorPalette.BG_DARK};
                color: {ColorPalette.TEXT_PRIMARY};
                border: none;
                border-radius: 6px;
                padding: 5px 10px;
            }}
        """)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(search_box)
        
        history_layout.addLayout(header_layout)
        
        # Transactions container in darker background - same as in main window
        transactions_container = QFrame()
        transactions_container.setStyleSheet(f"""
            background-color: {ColorPalette.CARD_BG_DARKER};
            border-radius: 8px;
        """)
        
        # Container layout
        container_layout = QVBoxLayout(transactions_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)  # No spacing for table items
        
        # Improved table to match the style of tables in your app
        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(6)
        self.transaction_table.setHorizontalHeaderLabels(["Date", "Type", "Stock", "Shares/Price", "Total", "Status"])
        
        # Table styling to match other tables in the app
        self.transaction_table.setShowGrid(False)
        self.transaction_table.setAlternatingRowColors(False)
        self.transaction_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.transaction_table.horizontalHeader().setStyleSheet(f"""
            QHeaderView::section {{
                background-color: {ColorPalette.CARD_BG_DARKER};
                color: {ColorPalette.TEXT_SECONDARY};
                border: none;
                padding: 10px;
                font-weight: bold;
                text-align: left;
            }}
        """)
        self.transaction_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: transparent;
                color: {ColorPalette.TEXT_PRIMARY};
                border: none;
                selection-background-color: {ColorPalette.ACCENT_PRIMARY}30;
                selection-color: {ColorPalette.TEXT_PRIMARY};
            }}
            QTableWidget::item {{
                border-bottom: 1px solid {ColorPalette.BORDER_DARK};
                padding: 10px;
            }}
            QTableWidget QTableCornerButton::section {{
                background-color: {ColorPalette.CARD_BG_DARKER};
                border: none;
            }}
        """)
        self.transaction_table.verticalHeader().setVisible(False)
        self.transaction_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.transaction_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.transaction_table.setFocusPolicy(Qt.NoFocus)
        self.transaction_table.setMinimumHeight(400)
        
        # Add table to container layout
        container_layout.addWidget(self.transaction_table)
        
        # Action buttons - same as other sections in the app
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(15, 15, 15, 15)
        
        view_all_btn = QPushButton("View All Transactions")
        view_all_btn.setStyleSheet(GlobalStyle.SECONDARY_BUTTON)
        view_all_btn.setCursor(Qt.PointingHandCursor)
        view_all_btn.setFixedHeight(36)
        
        export_btn = QPushButton("Export")
        export_btn.setStyleSheet(GlobalStyle.SECONDARY_BUTTON)
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.setFixedHeight(36)
        
        action_layout.addWidget(view_all_btn)
        action_layout.addStretch()
        action_layout.addWidget(export_btn)
        
        container_layout.addLayout(action_layout)
        
        history_layout.addWidget(transactions_container)
        
        self.content_layout.addWidget(history_card)
    
    def _setup_transaction_analysis_section(self):
        """Create transaction analysis section with summary metrics and charts"""
        section = QFrame()
        section_layout = QHBoxLayout(section)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(20)
        
        # Transaction Summary Card
        summary_card = self._create_transaction_summary_card()
        
        # Transaction Metrics Card
        metrics_card = self._create_transaction_metrics_card()
        
        # Add cards to section layout
        section_layout.addWidget(summary_card, 1)
        section_layout.addWidget(metrics_card, 1)
        
        self.content_layout.addWidget(section)
        
        # Store reference for responsive design
        self.analysis_section = section
        self.analysis_section_layout = section_layout
    
    def _create_transaction_summary_card(self):
        """Create transaction summary card with visualization"""
        # Card with same styling as main window
        card = QFrame()
        card.setStyleSheet(GlobalStyle.CARD_STYLE)
        
        # Shadow effect - exact match to main window
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)
        
        # Layout with same margins
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)
        
        # Title
        title = QLabel("Transaction Summary")
        title.setStyleSheet(GlobalStyle.SUBHEADER_STYLE)
        card_layout.addWidget(title)
        
        # Summary container
        summary_container = QFrame()
        summary_container.setStyleSheet(f"""
            background-color: {ColorPalette.CARD_BG_DARKER};
            border-radius: 8px;
        """)
        
        container_layout = QVBoxLayout(summary_container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(15)
        
        # Buy vs Sell visualization - pie chart
        chart_label = QLabel()
        chart_label.setFixedHeight(200)
        
        # Create buy/sell pie chart
        chart_pixmap = QPixmap(200, 200)
        chart_pixmap.fill(Qt.transparent)
        
        painter = QPainter(chart_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw pie slices
        center = QPoint(100, 100)
        radius = 80
        
        # Buy (65%)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(ColorPalette.ACCENT_SUCCESS))
        painter.drawPie(center.x() - radius, center.y() - radius, 
                      radius * 2, radius * 2, 
                      0, int(65 * 360 * 16 / 100))
        
        # Sell (35%)
        painter.setBrush(QColor(ColorPalette.ACCENT_DANGER))
        painter.drawPie(center.x() - radius, center.y() - radius, 
                      radius * 2, radius * 2, 
                      int(65 * 360 * 16 / 100), int(35 * 360 * 16 / 100))
        
        # Draw inner circle for donut effect
        painter.setBrush(QColor(ColorPalette.CARD_BG_DARKER))
        painter.drawEllipse(center, radius * 0.6, radius * 0.6)
        
        # Add center text
        painter.setPen(QColor(ColorPalette.TEXT_PRIMARY))
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        painter.setFont(font)
        painter.drawText(QRect(center.x() - 50, center.y() - 15, 100, 30), Qt.AlignCenter, "Buy/Sell Ratio")
        
        painter.end()
        chart_label.setPixmap(chart_pixmap)
        chart_label.setAlignment(Qt.AlignCenter)
        
        container_layout.addWidget(chart_label)
        
        # Legend and stats
        legend_layout = QHBoxLayout()
        
        # Buy legend
        buy_layout = QVBoxLayout()
        
        buy_header = QHBoxLayout()
        buy_color = QFrame()
        buy_color.setFixedSize(12, 12)
        buy_color.setStyleSheet(f"""
            background-color: {ColorPalette.ACCENT_SUCCESS};
            border-radius: 2px;
        """)
        
        buy_label = QLabel("Buy Orders")
        buy_label.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold;")
        
        buy_header.addWidget(buy_color)
        buy_header.addSpacing(8)
        buy_header.addWidget(buy_label)
        buy_header.addStretch()
        
        buy_stats = QGridLayout()
        buy_stats.setVerticalSpacing(5)
        buy_stats.setHorizontalSpacing(10)
        
        buy_count_label = QLabel("Count:")
        buy_count_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
        buy_count_value = QLabel("165")
        buy_count_value.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY};")
        
        buy_amount_label = QLabel("Total Amount:")
        buy_amount_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
        buy_amount_value = QLabel("$148,532.75")
        buy_amount_value.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY};")
        
        buy_stats.addWidget(buy_count_label, 0, 0)
        buy_stats.addWidget(buy_count_value, 0, 1)
        buy_stats.addWidget(buy_amount_label, 1, 0)
        buy_stats.addWidget(buy_amount_value, 1, 1)
        
        buy_layout.addLayout(buy_header)
        buy_layout.addLayout(buy_stats)
        
        # Sell legend
        sell_layout = QVBoxLayout()
        
        sell_header = QHBoxLayout()
        sell_color = QFrame()
        sell_color.setFixedSize(12, 12)
        sell_color.setStyleSheet(f"""
            background-color: {ColorPalette.ACCENT_DANGER};
            border-radius: 2px;
        """)
        
        sell_label = QLabel("Sell Orders")
        sell_label.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold;")
        
        sell_header.addWidget(sell_color)
        sell_header.addSpacing(8)
        sell_header.addWidget(sell_label)
        sell_header.addStretch()
        
        sell_stats = QGridLayout()
        sell_stats.setVerticalSpacing(5)
        sell_stats.setHorizontalSpacing(10)
        
        sell_count_label = QLabel("Count:")
        sell_count_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
        sell_count_value = QLabel("89")
        sell_count_value.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY};")
        
        sell_amount_label = QLabel("Total Amount:")
        sell_amount_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
        sell_amount_value = QLabel("$82,947.18")
        sell_amount_value.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY};")
        
        sell_stats.addWidget(sell_count_label, 0, 0)
        sell_stats.addWidget(sell_count_value, 0, 1)
        sell_stats.addWidget(sell_amount_label, 1, 0)
        sell_stats.addWidget(sell_amount_value, 1, 1)
        
        sell_layout.addLayout(sell_header)
        sell_layout.addLayout(sell_stats)
        
        legend_layout.addLayout(buy_layout)
        legend_layout.addSpacing(30)
        legend_layout.addLayout(sell_layout)
        
        container_layout.addLayout(legend_layout)
        
        # Summary metrics
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet(f"background-color: {ColorPalette.BORDER_DARK};")
        divider.setFixedHeight(1)
        
        container_layout.addWidget(divider)
        
        # Net cash flow
        cashflow_layout = QHBoxLayout()
        
        cashflow_label = QLabel("Net Cash Flow:")
        cashflow_label.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold;")
        
        cashflow_value = QLabel("-$65,585.57")
        cashflow_value.setStyleSheet(f"color: {ColorPalette.ACCENT_DANGER}; font-weight: bold; font-size: 18px;")
        
        cashflow_layout.addWidget(cashflow_label)
        cashflow_layout.addStretch()
        cashflow_layout.addWidget(cashflow_value)
        
        container_layout.addLayout(cashflow_layout)
        
        card_layout.addWidget(summary_container)
        
        return card
    
    def _create_transaction_metrics_card(self):
        """Create transaction metrics card with trends and insights"""
        # Card with same styling as main window
        card = QFrame()
        card.setStyleSheet(GlobalStyle.CARD_STYLE)
        
        # Shadow effect - exact match to main window
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)
        
        # Layout with same margins
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)
        
        # Title
        title = QLabel("Transaction Metrics")
        title.setStyleSheet(GlobalStyle.SUBHEADER_STYLE)
        card_layout.addWidget(title)
        
        # Metrics container
        metrics_container = QFrame()
        metrics_container.setStyleSheet(f"""
            background-color: {ColorPalette.CARD_BG_DARKER};
            border-radius: 8px;
        """)
        
        container_layout = QVBoxLayout(metrics_container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(20)
        
        # Transaction volume graph
        volume_layout = QVBoxLayout()
        
        volume_label = QLabel("Transaction Volume by Month")
        volume_label.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold;")
        
        volume_graph = QLabel()
        volume_graph.setFixedHeight(120)
        
        # Create bar graph for transaction volume
        pixmap = QPixmap(500, 120)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw bar graph
        bar_width = 30
        gap = 15
        bar_count = 12  # One for each month
        
        # Y-axis line
        painter.setPen(QPen(QColor(ColorPalette.BORDER_LIGHT), 1))
        painter.drawLine(30, 10, 30, 100)
        
        # X-axis line
        painter.drawLine(30, 100, 500, 100)
        
        # Draw bars
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        values = [23, 31, 42, 19, 28, 35, 30, 25, 34, 29, 45, 38]  # Sample data
        
        max_value = max(values)
        scale_factor = 80 / max_value  # 80px is the available height
        
        for i, value in enumerate(values):
            x = 50 + i * (bar_width + gap)
            bar_height = value * scale_factor
            y = 100 - bar_height
            
            # Main bar gradient
            gradient = QLinearGradient(0, y, 0, 100)
            gradient.setColorAt(0, QColor(ColorPalette.ACCENT_PRIMARY))
            gradient.setColorAt(1, QColor(ColorPalette.ACCENT_INFO))
            
            painter.setBrush(gradient)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(x, y, bar_width, bar_height, 4, 4)
            
            # Month label
            painter.setPen(QColor(ColorPalette.TEXT_SECONDARY))
            font = QFont()
            font.setPointSize(7)
            painter.setFont(font)
            painter.drawText(QRect(x - 5, 105, 40, 15), Qt.AlignCenter, months[i])
        
        painter.end()
        volume_graph.setPixmap(pixmap)
        
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(volume_graph)
        
        container_layout.addLayout(volume_layout)
        
        # Key metrics in a grid
        metrics_grid = QGridLayout()
        metrics_grid.setVerticalSpacing(15)
        metrics_grid.setHorizontalSpacing(30)
        
        metrics = [
            {"label": "Average Transaction", "value": "$843.21", "trend": "+5.4%", "positive": True},
            {"label": "Largest Purchase", "value": "$12,458.00", "trend": "AAPL", "positive": None},
            {"label": "Most Active Stock", "value": "TSLA", "trend": "24 trades", "positive": None},
            {"label": "Largest Sale", "value": "$8,743.92", "trend": "MSFT", "positive": None}
        ]
        
        for i, metric in enumerate(metrics):
            row = i // 2
            col = i % 2
            
            metric_widget = QWidget()
            metric_layout = QVBoxLayout(metric_widget)
            metric_layout.setContentsMargins(0, 0, 0, 0)
            metric_layout.setSpacing(3)
            
            # Label
            label = QLabel(metric["label"])
            label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
            
            # Value
            value = QLabel(metric["value"])
            value.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold; font-size: 18px;")
            
            # Trend
            trend_layout = QHBoxLayout()
            trend_layout.setContentsMargins(0, 0, 0, 0)
            trend_layout.setSpacing(5)
            
            trend = QLabel(metric["trend"])
            if metric["positive"] is not None:
                color = ColorPalette.ACCENT_SUCCESS if metric["positive"] else ColorPalette.ACCENT_DANGER
                trend.setStyleSheet(f"color: {color}; font-size: 12px;")
            else:
                trend.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
            
            trend_layout.addWidget(trend)
            trend_layout.addStretch()
            
            metric_layout.addWidget(label)
            metric_layout.addWidget(value)
            metric_layout.addLayout(trend_layout)
            
            metrics_grid.addWidget(metric_widget, row, col)
        
        container_layout.addLayout(metrics_grid)
        
        card_layout.addWidget(metrics_container)
        
        return card
    
    def _generate_sample_transactions(self):
        """Generate sample transaction data for the table that matches the style of other tables"""
        # Sample data for transactions
        transactions = [
            {"date": "Mar 07, 2025", "type": "Buy", "stock": "AAPL", "shares": 10, "price": 173.45, "total": 1734.50, "status": "Completed"},
            {"date": "Mar 05, 2025", "type": "Sell", "stock": "TSLA", "shares": 5, "price": 238.79, "total": 1193.95, "status": "Completed"},
            {"date": "Mar 02, 2025", "type": "Buy", "stock": "MSFT", "shares": 8, "price": 324.62, "total": 2596.96, "status": "Completed"},
            {"date": "Feb 28, 2025", "type": "Dividend", "stock": "JNJ", "shares": None, "price": None, "total": 134.50, "status": "Completed"},
            {"date": "Feb 25, 2025", "type": "Buy", "stock": "GOOGL", "shares": 12, "price": 139.78, "total": 1677.36, "status": "Completed"},
            {"date": "Feb 20, 2025", "type": "Sell", "stock": "AMZN", "shares": 4, "price": 128.91, "total": 515.64, "status": "Completed"},
            {"date": "Feb 18, 2025", "type": "Buy", "stock": "META", "shares": 15, "price": 302.55, "total": 4538.25, "status": "Completed"},
            {"date": "Feb 15, 2025", "type": "Deposit", "stock": None, "shares": None, "price": None, "total": 10000.00, "status": "Completed"},
            {"date": "Feb 10, 2025", "type": "Buy", "stock": "NVDA", "shares": 5, "price": 437.26, "total": 2186.30, "status": "Completed"},
            {"date": "Feb 05, 2025", "type": "Sell", "stock": "AAPL", "shares": 8, "price": 180.90, "total": 1447.20, "status": "Completed"}
        ]
        
        # Set up table
        self.transaction_table.setRowCount(len(transactions))
        
        # Create transaction items with styles that match your app's other tables
        for row, transaction in enumerate(transactions):
            # Date
            date_item = QTableWidgetItem(transaction["date"])
            date_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
            # Type with colored styling - same as in main window
            type_item = QTableWidgetItem()
            type_item.setText(transaction["type"])
            type_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
            # Set color based on transaction type
            if transaction["type"] == "Buy":
                type_item.setForeground(QColor(ColorPalette.ACCENT_SUCCESS))
            elif transaction["type"] == "Sell":
                type_item.setForeground(QColor(ColorPalette.ACCENT_DANGER))
            elif transaction["type"] == "Dividend":
                type_item.setForeground(QColor(ColorPalette.ACCENT_INFO))
            elif transaction["type"] == "Deposit":
                type_item.setForeground(QColor(ColorPalette.ACCENT_PRIMARY))
            elif transaction["type"] == "Withdrawal":
                type_item.setForeground(QColor(ColorPalette.ACCENT_WARNING))
            
            # Stock
            stock_item = QTableWidgetItem(transaction["stock"] if transaction["stock"] else "")
            stock_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
            # Shares/Price - combined column
            shares_price_text = ""
            if transaction["shares"] is not None and transaction["price"] is not None:
                shares_price_text = f"{transaction['shares']} shares @ ${transaction['price']:.2f}"
            shares_price_item = QTableWidgetItem(shares_price_text)
            shares_price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Total with dollar sign
            total_text = f"${transaction['total']:.2f}"
            if transaction["type"] == "Withdrawal":
                total_text = f"-{total_text}"  # Add negative sign for withdrawals
                
            total_item = QTableWidgetItem(total_text)
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Status with colored styling
            status_item = QTableWidgetItem(transaction["status"])
            
            # Style status based on value
            if transaction["status"] == "Completed":
                status_item.setForeground(QColor(ColorPalette.ACCENT_SUCCESS))
            elif transaction["status"] == "Pending":
                status_item.setForeground(QColor(ColorPalette.ACCENT_WARNING))
            elif transaction["status"] == "Failed":
                status_item.setForeground(QColor(ColorPalette.ACCENT_DANGER))
            elif transaction["status"] == "Canceled":
                status_item.setForeground(QColor(ColorPalette.TEXT_SECONDARY))
            
            # Add item action button (for the last row to demonstrate)
            if row == 0:
                # Create action button widget
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(0, 0, 0, 0)
                action_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                # Action button
                action_btn = QToolButton()
                action_btn.setText("⋮")  # Vertical ellipsis for menu
                action_btn.setCursor(Qt.PointingHandCursor)
                action_btn.setStyleSheet(f"""
                    QToolButton {{
                        background-color: transparent;
                        border: none;
                        padding: 2px;
                        color: {ColorPalette.TEXT_SECONDARY};
                        font-size: 16px;
                    }}
                    QToolButton:hover {{
                        background-color: {ColorPalette.BG_DARK};
                        border-radius: 4px;
                    }}
                """)
                
                # Create menu
                action_menu = QMenu()
                action_menu.setStyleSheet(f"""
                    QMenu {{
                        background-color: {ColorPalette.BG_CARD};
                        color: {ColorPalette.TEXT_PRIMARY};
                        border: 1px solid {ColorPalette.BORDER_DARK};
                        border-radius: 8px;
                        padding: 5px;
                    }}
                    QMenu::item {{
                        padding: 8px 15px;
                        border-radius: 4px;
                    }}
                    QMenu::item:selected {{
                        background-color: {ColorPalette.BG_DARK};
                    }}
                """)
                
                # Add actions
                action_sell = QAction("Sell", action_menu)
                action_buy = QAction("Buy More", action_menu)
                action_view = QAction("View Details", action_menu)
                
                action_menu.addAction(action_sell)
                action_menu.addAction(action_buy)
                action_menu.addSeparator()
                action_menu.addAction(action_view)
                
                action_btn.setMenu(action_menu)
                action_btn.setPopupMode(QToolButton.InstantPopup)
                
                action_layout.addWidget(action_btn)
                
                # Set the action_widget to the last column
                self.transaction_table.setCellWidget(row, 5, action_widget)
            else:
                self.transaction_table.setItem(row, 5, status_item)
            
            # Set items in the table
            self.transaction_table.setItem(row, 0, date_item)
            self.transaction_table.setItem(row, 1, type_item)
            self.transaction_table.setItem(row, 2, stock_item)
            self.transaction_table.setItem(row, 3, shares_price_item)
            self.transaction_table.setItem(row, 4, total_item)
            
            # Set row height
            self.transaction_table.setRowHeight(row, 50)  # Same row height as in main window
    
    def eventFilter(self, obj, event):
        """Handle resize events for responsive design"""
        if obj == self and event.type() == QEvent.Resize:
            self._adjust_responsive_layout()
        return super().eventFilter(obj, event)
    
    def _adjust_responsive_layout(self):
        """Adjust layout based on screen width - same responsive behavior as main window"""
        # Avoid recursive calls
        if hasattr(self, '_is_adjusting') and self._is_adjusting:
            return
        
        self._is_adjusting = True
        
        try:
            width = self.width()
            
            # For narrower screens - same breakpoint as main window
            is_narrow = width < 900
            
            # Adjust section layouts
            if hasattr(self, 'analysis_section_layout'):
                self._adjust_section_layout(self.analysis_section_layout, is_narrow)
            
            # Adjust content margins - same as main window
            if is_narrow:
                self.content_layout.setContentsMargins(10, 0, 10, 10)
            else:
                self.content_layout.setContentsMargins(20, 0, 20, 20)
                
        finally:
            # Use a timer to reset the flag to prevent deadlocks
            QTimer.singleShot(100, self._reset_adjusting_flag)
    
    def _reset_adjusting_flag(self):
        """Safely reset the adjusting flag after a delay"""
        self._is_adjusting = False
    
    def _adjust_section_layout(self, layout, is_narrow):
        """Helper method to adjust a section layout direction"""
        if not layout:
            return
            
        if is_narrow and layout.direction() != QBoxLayout.TopToBottom:
            layout.setDirection(QBoxLayout.TopToBottom)
        elif not is_narrow and layout.direction() != QBoxLayout.LeftToRight:
            layout.setDirection(QBoxLayout.LeftToRight)


# Main function to run the transactions page standalone
def main():
    app = QApplication(sys.argv)
    
    # Set app style
    app.setStyle("Fusion")
    
    # Create and show window
    window = QWidget()
    window.setWindowTitle("StockMaster Pro - Transactions")
    window.setMinimumSize(1000, 700)
    window.setStyleSheet(f"""
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
    
    layout = QVBoxLayout(window)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    
    transactions_page = TransactionsPage()
    layout.addWidget(transactions_page)
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()