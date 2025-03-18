import sys
import os
from datetime import datetime, timedelta
import random

from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QFrame, QHBoxLayout,
                               QLabel, QGridLayout, QScrollArea, QSizePolicy, QGraphicsDropShadowEffect,
                               QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QComboBox, 
                               QTabWidget, QStackedWidget, QBoxLayout, QToolButton, QMenu)
from PySide6.QtGui import (QColor, QAction, QFont, QPainter, QLinearGradient, QBrush, QPen,
                           QFontMetrics, QIcon, QPixmap, QCursor, QPainterPath, QRadialGradient)
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
        header.setMinimumHeight(130)  # Increased height for card layout
        header.setStyleSheet("background-color: transparent;")
        
        # Main layout
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)
        header_layout.setSpacing(15)
        
        # Title and subtitle row
        title_row = QHBoxLayout()
        
        # Title and subtitle - same styling as main window
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)
        
        title = QLabel("Transaction History")
        title.setStyleSheet(GlobalStyle.HEADER_STYLE)
        
        subtitle = QLabel("Track and analyze your investment activities")
        subtitle.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 14px;")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        # Period selector (new)
        period_selector = QComboBox()
        period_selector.addItems(["Last 30 Days", "Last 90 Days", "Last 6 Months", "Year to Date", "All Time"])
        period_selector.setCurrentIndex(0)  # Default to 30 days
        period_selector.setFixedWidth(150)
        period_selector.setStyleSheet(f"""
            QComboBox {{
                background-color: {ColorPalette.BG_DARK};
                color: {ColorPalette.TEXT_PRIMARY};
                border: 1px solid {ColorPalette.BORDER_DARK};
                border-radius: 6px;
                padding: 6px 10px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
        """)
        
        title_row.addLayout(title_layout)
        title_row.addStretch(1)
        title_row.addWidget(period_selector)
        
        header_layout.addLayout(title_row)
        
        # KPI Cards in horizontal layout
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(15)
        
        # Calculate metrics dynamically from transaction data
        total_transactions = len(self.user_transactions)
        buy_orders = sum(1 for tx in self.user_transactions if tx['transactionType'].lower() == 'buy')
        sell_orders = sum(1 for tx in self.user_transactions if tx['transactionType'].lower() == 'sell')
        total_volume = sum(tx.get('price', 0) * tx.get('quantity', 0) 
                        for tx in self.user_transactions 
                        if 'price' in tx and 'quantity' in tx)
        
        # KPI card data
        kpi_cards = [
            {
                "title": "Total Transactions",
                "value": f"{total_transactions:,}",
                "icon": "Icons/transaction.png",
                "color": ColorPalette.ACCENT_PRIMARY,
                "subtitle": "Last 30 days",
                "change": "+12%"
            },
            {
                "title": "Buying Power",
                "value": f"${self.balance:,.2f}" if self.balance is not None else "N/A",
                "icon": "Icons/wallet.png",
                "color": ColorPalette.ACCENT_SUCCESS,
                "subtitle": "Available to trade",
                "change": None
            },
            {
                "title": "Transaction Volume",
                "value": f"${total_volume:,.2f}",
                "icon": "Icons/chart.png",
                "color": ColorPalette.ACCENT_INFO,
                "subtitle": "Total traded value",
                "change": "-5.2%"
            },
            {
                "title": "Buy/Sell Ratio",
                "value": f"{buy_orders:,}/{sell_orders:,}",
                "icon": "Icons/exchange.png",
                "color": ColorPalette.ACCENT_WARNING,
                "subtitle": "Buy vs. Sell orders",
                "change": "+3.1%"
            }
        ]
        
        # Create each KPI card
        for kpi in kpi_cards:
            # Card frame
            card = QFrame()
            card.setStyleSheet(f"""
                background-color: {ColorPalette.BG_CARD};
                border-radius: 12px;
            """)
            
            # Card shadow
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setColor(QColor(0, 0, 0, 30))
            shadow.setOffset(0, 3)
            card.setGraphicsEffect(shadow)
            
            # Card layout
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(15, 12, 15, 12)
            card_layout.setSpacing(12)
            
            # Icon placeholder (you would replace with actual icon)
            icon_frame = QFrame()
            icon_frame.setFixedSize(36, 36)
            icon_frame.setStyleSheet(f"""
                background-color: {kpi['color']}30;
                border-radius: 8px;
            """)
            icon_layout = QVBoxLayout(icon_frame)
            icon_layout.setContentsMargins(0, 0, 0, 0)
            icon_layout.setAlignment(Qt.AlignCenter)
            
            # Uncomment and use if you have actual icons
            # icon_label = QLabel()
            # icon_pixmap = QPixmap(kpi['icon'])
            # icon_label.setPixmap(icon_pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            # icon_layout.addWidget(icon_label)
            
            # Text content
            text_layout = QVBoxLayout()
            text_layout.setSpacing(2)
            
            # Title
            title_label = QLabel(kpi["title"])
            title_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
            
            # Value and change row
            value_row = QHBoxLayout()
            value_row.setSpacing(6)
            
            value_label = QLabel(kpi["value"])
            value_label.setStyleSheet(f"""
                color: {ColorPalette.TEXT_PRIMARY}; 
                font-size: 18px; 
                font-weight: bold;
            """)
            
            value_row.addWidget(value_label)
            
            # Add change indicator if present
            if kpi["change"]:
                change_label = QLabel(kpi["change"])
                
                # Set color based on if change is positive or negative
                change_color = ColorPalette.ACCENT_SUCCESS if kpi["change"].startswith("+") else ColorPalette.ACCENT_DANGER
                change_label.setStyleSheet(f"color: {change_color}; font-size: 12px;")
                
                value_row.addWidget(change_label)
            
            value_row.addStretch()
            
            # Subtitle
            subtitle_label = QLabel(kpi["subtitle"])
            subtitle_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 11px;")
            
            # Add widgets to text layout
            text_layout.addWidget(title_label)
            text_layout.addLayout(value_row)
            text_layout.addWidget(subtitle_label)
            
            # Add to card layout
            card_layout.addWidget(icon_frame)
            card_layout.addLayout(text_layout)
            
            # Add card to layout with equal stretch
            kpi_layout.addWidget(card, 1)
        
        header_layout.addLayout(kpi_layout)
        
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

    def _export_transactions_to_csv(self):
        """Export transaction data to a CSV file"""
        try:
            # Skip if no transactions
            if not self.user_transactions:
                # Show a message dialog
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Export Transactions", 
                                    "No transactions available to export.",
                                    QMessageBox.Ok)
                return

            # Get file path from save dialog
            from PySide6.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Transactions",
                "transaction_history.csv",
                "CSV Files (*.csv)"
            )
            
            # Return if user cancels the dialog
            if not file_path:
                return
                
            # Add .csv extension if not provided
            if not file_path.endswith('.csv'):
                file_path += '.csv'
                
            # Convert transaction data to a consistent format for CSV export
            export_data = []
            
            for tx in self.user_transactions:
                # Process the date to a consistent format
                try:
                    date_str = tx['date']
                    
                    # Handle multiple date formats
                    if 'T' in date_str:
                        # ISO format
                        if '.' in date_str:  # Has microseconds
                            base, ms_part = date_str.split('.')
                            # Remove timezone info and Z if present
                            ms_part = ms_part.rstrip('Z').split('+')[0].split('-')[0]
                            date_str = f"{base}.{ms_part}"
                            
                        try:
                            tx_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
                        except ValueError:
                            try:
                                tx_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
                            except ValueError:
                                tx_date = datetime.now()  # Fallback
                    else:
                        # Other formats
                        for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%b %d, %Y"]:
                            try:
                                tx_date = datetime.strptime(date_str, fmt)
                                break
                            except ValueError:
                                continue
                        else:
                            tx_date = datetime.now()  # Fallback
                    
                    formatted_date = tx_date.strftime("%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    print(f"Error formatting date: {e}")
                    formatted_date = tx.get('date', 'Unknown')
                
                # Calculate the total amount if price and quantity are available
                total_amount = 0
                if 'price' in tx and 'quantity' in tx and tx['price'] is not None and tx['quantity'] is not None:
                    total_amount = tx['price'] * tx['quantity']
                elif 'amount' in tx and tx['amount'] is not None:
                    total_amount = tx['amount']
                
                # Get stock name if available
                stock_symbol = tx.get('stockSymbol', '')
                stock_name = stock_symbol
                
                if stock_symbol and self.stocks_the_user_has and stock_symbol in self.stocks_the_user_has:
                    stock_name = self.stocks_the_user_has[stock_symbol].get('name', stock_symbol)
                
                # Create a row for the CSV
                row = {
                    'Date': formatted_date,
                    'Type': tx.get('transactionType', 'Unknown'),
                    'Symbol': stock_symbol,
                    'Company': stock_name if stock_name != stock_symbol else '',
                    'Quantity': tx.get('quantity', ''),
                    'Price': f"${tx.get('price', 0):.2f}" if 'price' in tx and tx['price'] is not None else '',
                    'Total': f"${total_amount:.2f}" if total_amount else '',
                    'Status': 'Completed'  # Default status
                }
                
                export_data.append(row)
            
            # Write to CSV file
            import csv
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                # Define CSV columns
                fieldnames = ['Date', 'Type', 'Symbol', 'Company', 'Quantity', 'Price', 'Total', 'Status']
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in export_data:
                    writer.writerow(row)
            
            # Show success message
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Export Successful", 
                                f"Transaction history exported to {file_path}",
                                QMessageBox.Ok)
                                
        except Exception as e:
            # Show error message
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Export Error", 
                                f"Failed to export transactions: {str(e)}",
                                QMessageBox.Ok)
            print(f"Error exporting transactions: {e}")

    # Update the _setup_transaction_history_section to connect the export button
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
        
        # Filter dropdown to replace search box
        filter_combo = QComboBox()
        filter_combo.addItems(["All Transactions", "Buy Orders", "Sell Orders", "Deposits", "Withdrawals", "Dividends"])
        filter_combo.setFixedWidth(200)
        filter_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {ColorPalette.BG_DARK};
                color: {ColorPalette.TEXT_PRIMARY};
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                min-height: 36px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox::down-arrow {{
                image: url(Icons/dropdown_arrow.png);
                width: 12px;
                height: 12px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {ColorPalette.BG_DARK};
                color: {ColorPalette.TEXT_PRIMARY};
                border: 1px solid {ColorPalette.BORDER_DARK};
                border-radius: 6px;
                selection-background-color: {ColorPalette.ACCENT_PRIMARY}30;
            }}
        """)
        
        search_box = QLineEdit()
        search_box.setPlaceholderText("Search transactions...")
        search_box.setFixedWidth(200)
        search_box.setStyleSheet(f"""
            QLineEdit {{
                background-color: {ColorPalette.BG_DARK};
                color: {ColorPalette.TEXT_PRIMARY};
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                min-height: 36px;
            }}
        """)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(filter_combo)
        header_layout.addSpacing(10)
        header_layout.addWidget(search_box)
        
        history_layout.addLayout(header_layout)
        
        # Transactions container in darker background - same as in main window
        transactions_container = QFrame()
        transactions_container.setStyleSheet(f"""
            background-color: {ColorPalette.CARD_BG_DARKER};
            border-radius: 12px;  /* Increased radius for modern look */
        """)
        
        # Container layout
        container_layout = QVBoxLayout(transactions_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)  # No spacing for table items
        
        # Improved table to match the style of tables in your app
        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(6)
        self.transaction_table.setHorizontalHeaderLabels(["Date", "Type", "Stock", "Shares/Price", "Total", "Status"])
        
        # Table styling to match other tables in the app but with modernized look
        self.transaction_table.setShowGrid(False)
        self.transaction_table.setAlternatingRowColors(True)  # Enable alternating row colors
        self.transaction_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.transaction_table.horizontalHeader().setStyleSheet(f"""
            QHeaderView::section {{
                background-color: {ColorPalette.CARD_BG_DARKER};
                color: {ColorPalette.TEXT_SECONDARY};
                border: none;
                padding: 12px;  /* Increased padding */
                font-weight: bold;
                text-align: left;
                border-bottom: 2px solid {ColorPalette.BORDER_DARK};  /* More prominent header */
            }}
        """)
        self.transaction_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: transparent;
                color: {ColorPalette.TEXT_PRIMARY};
                border: none;
                selection-background-color: {ColorPalette.ACCENT_PRIMARY}20;  /* Lighter selection */
                selection-color: {ColorPalette.TEXT_PRIMARY};
                alternate-background-color: {ColorPalette.BG_DARK}30;  /* Subtle alternating color */
            }}
            QTableWidget::item {{
                border-bottom: 1px solid {ColorPalette.BORDER_DARK}40;  /* Lighter border */
                padding: 12px;  /* Increased padding */
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
        
        # Action buttons - updated with more emphasis on primary action
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(15, 15, 15, 15)
        
        view_all_btn = QPushButton("View All Transactions")
        view_all_btn.setStyleSheet(GlobalStyle.PRIMARY_BUTTON)  # Changed to primary button for emphasis
        view_all_btn.setCursor(Qt.PointingHandCursor)
        view_all_btn.setFixedHeight(36)
        
        export_btn = QPushButton("Export CSV")  # Added file format for clarity
        export_btn.setStyleSheet(GlobalStyle.SECONDARY_BUTTON)
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.setFixedHeight(36)
        
        # Connect the export button to the export function
        export_btn.clicked.connect(self._export_transactions_to_csv)
        
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

        
        # Add cards to section layout
        section_layout.addWidget(summary_card, 2)

        
        self.content_layout.addWidget(section)
        
        # Store reference for responsive design
        self.analysis_section = section
        self.analysis_section_layout = section_layout
    
    def _create_transaction_summary_card(self):
        """Create transaction summary card with improved visualization"""
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
        
        # Header with title and period selector
        header_layout = QHBoxLayout()
        
        title = QLabel("Transaction Summary")
        title.setStyleSheet(GlobalStyle.SUBHEADER_STYLE)
        
        period_selector = QComboBox()
        period_selector.addItems(["1W", "1M", "3M", "6M", "1Y", "All"])
        period_selector.setCurrentIndex(1)  # Default to 1 month
        period_selector.setFixedWidth(100)
        period_selector.setStyleSheet(f"""
            QComboBox {{
                background-color: {ColorPalette.BG_DARK};
                color: {ColorPalette.TEXT_PRIMARY};
                border: 1px solid {ColorPalette.BORDER_DARK};
                border-radius: 6px;
                padding: 4px 8px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
        """)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(period_selector)
        
        card_layout.addLayout(header_layout)
        
        # Summary container
        summary_container = QFrame()
        summary_container.setStyleSheet(f"""
            background-color: {ColorPalette.CARD_BG_DARKER};
            border-radius: 12px;
        """)
        
        container_layout = QVBoxLayout(summary_container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(20)
        
        # Modern donut chart with gradient
        chart_label = QLabel()
        chart_label.setFixedHeight(220)
        
        # Create buy/sell donut chart with gradient
        chart_pixmap = QPixmap(220, 220)
        chart_pixmap.fill(Qt.transparent)
        
        painter = QPainter(chart_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw donut chart with gradients
        center = QPoint(110, 110)
        outer_radius = 90
        inner_radius = 45
        
        # Calculate actual percentages from transaction data
        buy_count = sum(1 for tx in self.user_transactions if tx['transactionType'].lower() == 'buy')
        sell_count = sum(1 for tx in self.user_transactions if tx['transactionType'].lower() == 'sell')
        
        total_count = buy_count + sell_count
        if total_count == 0:
            buy_percent = 50
            sell_percent = 50
        else:
            buy_percent = (buy_count / total_count) * 100
            sell_percent = (sell_count / total_count) * 100
        
        # Buy slice with gradient (green)
        buy_gradient = QLinearGradient(center.x() - outer_radius, center.y(), center.x() + outer_radius, center.y())
        buy_gradient.setColorAt(0, QColor(ColorPalette.ACCENT_SUCCESS))
        buy_gradient.setColorAt(1, QColor("#60c5ba"))  # Lighter teal-green
        
        painter.setBrush(buy_gradient)
        painter.setPen(Qt.NoPen)
        painter.drawPie(center.x() - outer_radius, center.y() - outer_radius, 
                    outer_radius * 2, outer_radius * 2, 
                    0, int(buy_percent * 360 * 16 / 100))
        
        # Sell slice with gradient (red)
        sell_gradient = QLinearGradient(center.x() - outer_radius, center.y(), center.x() + outer_radius, center.y())
        sell_gradient.setColorAt(0, QColor(ColorPalette.ACCENT_DANGER))
        sell_gradient.setColorAt(1, QColor("#ff7e67"))  # Lighter coral-red
        
        painter.setBrush(sell_gradient)
        painter.drawPie(center.x() - outer_radius, center.y() - outer_radius, 
                    outer_radius * 2, outer_radius * 2, 
                    int(buy_percent * 360 * 16 / 100), int(sell_percent * 360 * 16 / 100))
        
        # Draw inner circle for donut effect with glassy effect
        inner_gradient = QRadialGradient(center, inner_radius)
        inner_gradient.setColorAt(0, QColor(ColorPalette.CARD_BG_DARKER).lighter(110))
        inner_gradient.setColorAt(1, QColor(ColorPalette.CARD_BG_DARKER))
        
        painter.setBrush(inner_gradient)
        painter.drawEllipse(center, inner_radius, inner_radius)
        
        # Add center text
        painter.setPen(QColor(ColorPalette.TEXT_PRIMARY))
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        painter.setFont(font)
        
        # Show the buy percentage as the main value
        painter.drawText(QRect(center.x() - 40, center.y() - 25, 80, 25), Qt.AlignCenter, f"{buy_percent:.1f}%")
        
        font.setPointSize(9)
        font.setBold(False)
        painter.setFont(font)
        painter.setPen(QColor(ColorPalette.TEXT_SECONDARY))
        painter.drawText(QRect(center.x() - 40, center.y() + 5, 80, 20), Qt.AlignCenter, "Buy Orders")
        
        painter.end()
        chart_label.setPixmap(chart_pixmap)
        chart_label.setAlignment(Qt.AlignCenter)
        
        container_layout.addWidget(chart_label)
        
        # Legend and stats in a cleaner layout
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(30)
        
        # Buy stats in a clean card
        buy_card = QFrame()
        buy_card.setStyleSheet(f"""
            background-color: {ColorPalette.BG_DARK}50;
            border-radius: 8px;
        """)
        
        buy_layout = QVBoxLayout(buy_card)
        buy_layout.setContentsMargins(15, 12, 15, 12)
        buy_layout.setSpacing(8)
        
        buy_header = QHBoxLayout()
        buy_label = QLabel("Buy Orders")
        buy_label.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold;")
        
        buy_header.addWidget(buy_label)
        
        buy_layout.addLayout(buy_header)
        
        # Calculate buy order statistics
        buy_orders = [tx for tx in self.user_transactions if tx['transactionType'].lower() == 'buy']
        buy_total = sum(tx.get('price', 0) * tx.get('quantity', 0) 
                        for tx in buy_orders 
                        if 'price' in tx and 'quantity' in tx)
        
        # Buy stats
        buy_count_row = QHBoxLayout()
        buy_count_label = QLabel("Count:")
        buy_count_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
        buy_count_value = QLabel(f"{len(buy_orders)}")
        buy_count_value.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold;")
        
        buy_count_row.addWidget(buy_count_label)
        buy_count_row.addStretch()
        buy_count_row.addWidget(buy_count_value)
        
        buy_amount_row = QHBoxLayout()
        buy_amount_label = QLabel("Total Amount:")
        buy_amount_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
        buy_amount_value = QLabel(f"${buy_total:,.2f}")
        buy_amount_value.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold;")
        
        buy_amount_row.addWidget(buy_amount_label)
        buy_amount_row.addStretch()
        buy_amount_row.addWidget(buy_amount_value)
        
        buy_layout.addLayout(buy_count_row)
        buy_layout.addLayout(buy_amount_row)
        
        # Sell stats in a clean card
        sell_card = QFrame()
        sell_card.setStyleSheet(f"""
            background-color: {ColorPalette.BG_DARK}50;
            border-radius: 8px;
        """)
        
        sell_layout = QVBoxLayout(sell_card)
        sell_layout.setContentsMargins(15, 12, 15, 12)
        sell_layout.setSpacing(8)
        
        sell_header = QHBoxLayout()
        sell_label = QLabel("Sell Orders")
        sell_label.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold;")
        
        sell_header.addWidget(sell_label)
        
        sell_layout.addLayout(sell_header)
        
        # Calculate sell order statistics
        sell_orders = [tx for tx in self.user_transactions if tx['transactionType'].lower() == 'sell']
        sell_total = sum(tx.get('price', 0) * tx.get('quantity', 0) 
                        for tx in sell_orders 
                        if 'price' in tx and 'quantity' in tx)
        
        # Sell stats
        sell_count_row = QHBoxLayout()
        sell_count_label = QLabel("Count:")
        sell_count_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
        sell_count_value = QLabel(f"{len(sell_orders)}")
        sell_count_value.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold;")
        
        sell_count_row.addWidget(sell_count_label)
        sell_count_row.addStretch()
        sell_count_row.addWidget(sell_count_value)
        
        sell_amount_row = QHBoxLayout()
        sell_amount_label = QLabel("Total Amount:")
        sell_amount_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
        sell_amount_value = QLabel(f"${sell_total:,.2f}")
        sell_amount_value.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold;")
        
        sell_amount_row.addWidget(sell_amount_label)
        sell_amount_row.addStretch()
        sell_amount_row.addWidget(sell_amount_value)
        
        sell_layout.addLayout(sell_count_row)
        sell_layout.addLayout(sell_amount_row)
        
        stats_layout.addWidget(buy_card, 1)
        stats_layout.addWidget(sell_card, 1)
        
        container_layout.addLayout(stats_layout)
        


        
        card_layout.addWidget(summary_container)
        
        return card
    
    def _create_transaction_metrics_card(self):
        """Create transaction metrics card with timeline and insights based on actual data"""
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
        
        # Header with title and view options
        header_layout = QHBoxLayout()
        
        title = QLabel("Transaction Activity")
        title.setStyleSheet(GlobalStyle.SUBHEADER_STYLE)
        
        # View toggle buttons
        view_options = QFrame()
        view_options.setStyleSheet(f"""
            background-color: {ColorPalette.BG_DARK};
            border-radius: 6px;
        """)
        
        options_layout = QHBoxLayout(view_options)
        options_layout.setContentsMargins(2, 2, 2, 2)
        options_layout.setSpacing(0)
        
        count_btn = QPushButton("Count")
        count_btn.setCheckable(True)
        count_btn.setChecked(True)
        count_btn.setFixedHeight(28)
        count_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {ColorPalette.TEXT_SECONDARY};
                border: none;
                border-radius: 5px;
                padding: 4px 12px;
                font-size: 12px;
            }}
            QPushButton:checked {{
                background-color: {ColorPalette.ACCENT_PRIMARY};
                color: white;
            }}
        """)
        
        volume_btn = QPushButton("Volume")
        volume_btn.setCheckable(True)
        volume_btn.setFixedHeight(28)
        volume_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {ColorPalette.TEXT_SECONDARY};
                border: none;
                border-radius: 5px;
                padding: 4px 12px;
                font-size: 12px;
            }}
            QPushButton:checked {{
                background-color: {ColorPalette.ACCENT_PRIMARY};
                color: white;
            }}
        """)
        
        options_layout.addWidget(count_btn)
        options_layout.addWidget(volume_btn)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(view_options)
        
        card_layout.addLayout(header_layout)
        
        # Activity container
        metrics_container = QFrame()
        metrics_container.setStyleSheet(f"""
            background-color: {ColorPalette.CARD_BG_DARKER};
            border-radius: 12px;
        """)
        
        container_layout = QVBoxLayout(metrics_container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(20)
        
        # Process and analyze transaction data
        monthly_data = self._analyze_monthly_transactions()
        
        # Transaction activity timeline graph
        timeline_graph = QLabel()
        timeline_graph.setFixedHeight(180)
        
        # Create a timeline chart with actual data
        pixmap = QPixmap(540, 180)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Set up chart area
        chart_width = 520
        chart_height = 140
        margin_left = 40
        margin_top = 10
        margin_bottom = 30
        
        # Chart area background with subtle grid
        grid_color = QColor(ColorPalette.BORDER_DARK)
        grid_color.setAlpha(30)
        painter.setPen(QPen(grid_color, 1, Qt.DashLine))
        
        # Draw grid lines
        for i in range(5):
            y = margin_top + i * chart_height / 4
            painter.drawLine(margin_left, y, margin_left + chart_width, y)
        
        # Extract months and data from processed data
        months = list(monthly_data.keys())
        buy_values = [monthly_data[month]["buy_count"] for month in months]
        sell_values = [monthly_data[month]["sell_count"] for month in months]
        
        # If we don't have enough data, add some placeholders to make the chart look nice
        if len(months) < 2:
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
            buy_values = [0, 0, 0, 0, 0, 0]
            sell_values = [0, 0, 0, 0, 0, 0]
            
            # Add actual data if we have any
            if monthly_data:
                first_month = list(monthly_data.keys())[0]
                months[0] = first_month
                buy_values[0] = monthly_data[first_month]["buy_count"]
                sell_values[0] = monthly_data[first_month]["sell_count"]
        
        # Calculate x spacing
        x_step = chart_width / (len(months) - 1) if len(months) > 1 else chart_width
        
        # Find max value for scaling (with a minimum of 5 to prevent division by zero)
        max_value = max(max(buy_values + sell_values, default=0), 5)
        y_scale = chart_height / max_value if max_value > 0 else 1
        
        # X axis
        painter.setPen(QPen(QColor(ColorPalette.BORDER_LIGHT), 1))
        painter.drawLine(
            margin_left, margin_top + chart_height,
            margin_left + chart_width, margin_top + chart_height
        )
        
        # Month labels
        painter.setPen(QColor(ColorPalette.TEXT_SECONDARY))
        font = QFont()
        font.setPointSize(8)
        painter.setFont(font)
        
        for i, month in enumerate(months):
            x = margin_left + i * x_step
            painter.drawText(
                QRect(x - 15, margin_top + chart_height + 5, 30, 20),
                Qt.AlignCenter, month
            )
        
        # Draw buy line (gradient fill underneath)
        buy_points = []
        for i, value in enumerate(buy_values):
            x = margin_left + i * x_step
            y = margin_top + chart_height - (value * y_scale)
            buy_points.append(QPointF(x, y))
        
        # Only create path and draw if we have points
        if buy_points:
            # Create gradient for buy area
            buy_gradient = QLinearGradient(
                0, margin_top, 0, margin_top + chart_height
            )
            buy_color_start = QColor(ColorPalette.ACCENT_PRIMARY)
            buy_color_start.setAlpha(100)
            buy_color_end = QColor(ColorPalette.ACCENT_PRIMARY)
            buy_color_end.setAlpha(0)
            buy_gradient.setColorAt(0, buy_color_start)
            buy_gradient.setColorAt(1, buy_color_end)
            
            # Create path for buy area
            buy_path = QPainterPath()
            buy_path.moveTo(buy_points[0].x(), margin_top + chart_height)
            for point in buy_points:
                buy_path.lineTo(point)
            buy_path.lineTo(buy_points[-1].x(), margin_top + chart_height)
            
            # Fill buy area
            painter.fillPath(buy_path, buy_gradient)
            
            # Draw buy line
            painter.setPen(QPen(QColor(ColorPalette.ACCENT_PRIMARY), 2))
            for i in range(len(buy_points) - 1):
                painter.drawLine(buy_points[i], buy_points[i + 1])
            
            # Draw data points for buy line
            painter.setBrush(QColor(ColorPalette.BG_DARK))
            for point in buy_points:
                painter.drawEllipse(point, 4, 4)
        
        # Draw sell line (no fill)
        sell_points = []
        for i, value in enumerate(sell_values):
            x = margin_left + i * x_step
            y = margin_top + chart_height - (value * y_scale)
            sell_points.append(QPointF(x, y))
        
        # Only draw if we have points
        if sell_points:
            # Draw sell line
            painter.setPen(QPen(QColor(ColorPalette.ACCENT_DANGER), 2, Qt.SolidLine))
            for i in range(len(sell_points) - 1):
                painter.drawLine(sell_points[i], sell_points[i + 1])
            
            # Draw data points for sell line
            painter.setBrush(QColor(ColorPalette.BG_DARK))
            for point in sell_points:
                painter.drawEllipse(point, 4, 4)
        
        # Draw legend
        legend_y = margin_top + chart_height + 20
        
        # Buy legend
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(ColorPalette.ACCENT_PRIMARY))
        painter.drawRect(margin_left, legend_y, 12, 4)
        
        painter.setPen(QColor(ColorPalette.TEXT_SECONDARY))
        painter.drawText(
            QRect(margin_left + 18, legend_y - 5, 50, 15),
            Qt.AlignLeft | Qt.AlignVCenter, "Buy Orders"
        )
        
        # Sell legend
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(ColorPalette.ACCENT_DANGER))
        painter.drawRect(margin_left + 100, legend_y, 12, 4)
        
        painter.setPen(QColor(ColorPalette.TEXT_SECONDARY))
        painter.drawText(
            QRect(margin_left + 118, legend_y - 5, 50, 15),
            Qt.AlignLeft | Qt.AlignVCenter, "Sell Orders"
        )
        
        painter.end()
        timeline_graph.setPixmap(pixmap)
        
        container_layout.addWidget(timeline_graph)
        
        # Calculate real metrics from transaction data
        transaction_metrics = self._calculate_transaction_metrics()
        
        # Key metrics in cards using actual data
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(15)
        
        # Create each metric card using real data
        for metric in transaction_metrics:
            # Metric card
            metric_card = QFrame()
            # Fix: Use correct way to set background with alpha
            metric_card.setStyleSheet(f"""
                background-color: {ColorPalette.BG_DARK}40;
                border-radius: 8px;
                border-top: 3px solid {metric['color']};
            """)
            
            metric_layout = QVBoxLayout(metric_card)
            metric_layout.setContentsMargins(15, 12, 15, 12)
            metric_layout.setSpacing(3)
            
            # Metric label
            label = QLabel(metric["label"])
            label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
            
            # Metric value
            value = QLabel(metric["value"])
            value.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold; font-size: 18px;")
            
            # Metric detail
            detail = QLabel(metric["detail"])
            detail.setStyleSheet(f"color: {metric['color']}; font-size: 12px;")
            
            metric_layout.addWidget(label)
            metric_layout.addWidget(value)
            metric_layout.addWidget(detail)
            
            metrics_layout.addWidget(metric_card, 1)
        
        container_layout.addLayout(metrics_layout)
        
        card_layout.addWidget(metrics_container)
        
        return card
    

    def _analyze_monthly_transactions(self):
        """Analyze transactions by month to generate chart data"""
        # Dictionary to store monthly data
        monthly_data = {}
        
        try:
            # Process each transaction
            for tx in self.user_transactions:
                # Try to parse the date
                try:
                    # Handle different date formats
                    if 'date' in tx:
                        date_str = tx['date']
                        
                        # Convert string to datetime
                        if 'T' in date_str:  # ISO format
                            if '.' in date_str:  # Has microseconds
                                base, ms_part = date_str.split('.')
                                # Remove timezone info and Z if present
                                ms_part = ms_part.rstrip('Z').split('+')[0].split('-')[0]
                                # Ensure microseconds have exactly 6 digits
                                ms_part = ms_part.ljust(6, '0')[:6]
                                date_str = f"{base}.{ms_part}"
                            
                            try:
                                tx_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
                            except ValueError:
                                tx_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
                        else:  # Other formats
                            # Try different formats
                            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%b %d, %Y"]:
                                try:
                                    tx_date = datetime.strptime(date_str, fmt)
                                    break
                                except ValueError:
                                    continue
                            else:
                                # If all formats fail, skip this transaction
                                continue
                    else:
                        # Skip if no date
                        continue
                    
                    # Extract month for grouping
                    month_key = tx_date.strftime("%b")
                    
                    # Initialize month data if needed
                    if month_key not in monthly_data:
                        monthly_data[month_key] = {
                            "buy_count": 0,
                            "sell_count": 0,
                            "buy_volume": 0.0,
                            "sell_volume": 0.0,
                            "transactions": []
                        }
                    
                    # Add transaction to the monthly data
                    monthly_data[month_key]["transactions"].append(tx)
                    
                    # Update counts based on transaction type
                    tx_type = tx.get('transactionType', '').lower()
                    if tx_type == 'buy':
                        monthly_data[month_key]["buy_count"] += 1
                        # Calculate volume if price and quantity are available
                        if 'price' in tx and 'quantity' in tx:
                            monthly_data[month_key]["buy_volume"] += tx['price'] * tx['quantity']
                    elif tx_type == 'sell':
                        monthly_data[month_key]["sell_count"] += 1
                        # Calculate volume if price and quantity are available
                        if 'price' in tx and 'quantity' in tx:
                            monthly_data[month_key]["sell_volume"] += tx['price'] * tx['quantity']
                    
                except Exception as e:
                    print(f"Error processing transaction date: {e}")
                    continue
        
        except Exception as e:
            print(f"Error analyzing monthly transactions: {e}")
        
        return monthly_data

    def _calculate_transaction_metrics(self):
        """Calculate real metrics from transaction data"""
        metrics = []
        
        try:
            # Process all transactions to determine patterns
            transaction_dates = []
            transaction_amounts = []
            stock_counts = {}
            
            # Group transactions by day of week
            day_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
            day_names = {
                0: "Monday", 1: "Tuesday", 2: "Wednesday", 
                3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"
            }
            
            # Count transaction types
            buy_count = 0
            sell_count = 0
            
            for tx in self.user_transactions:
                # Try to get the date
                if 'date' in tx:
                    try:
                        # Parse date (simplified for this function)
                        date_str = tx['date']
                        if 'T' in date_str:
                            try:
                                tx_date = datetime.strptime(date_str.split('T')[0], "%Y-%m-%d")
                            except:
                                continue
                        else:
                            try:
                                tx_date = datetime.strptime(date_str, "%Y-%m-%d")
                            except:
                                try:
                                    tx_date = datetime.strptime(date_str, "%b %d, %Y")
                                except:
                                    continue
                        
                        transaction_dates.append(tx_date)
                        
                        # Count by day of week
                        day_of_week = tx_date.weekday()  # 0 = Monday, 6 = Sunday
                        day_counts[day_of_week] += 1
                        
                    except Exception as e:
                        print(f"Error parsing transaction date: {e}")
                
                # Count transaction types
                tx_type = tx.get('transactionType', '').lower()
                if tx_type == 'buy':
                    buy_count += 1
                elif tx_type == 'sell':
                    sell_count += 1
                
                # Get transaction amount
                amount = 0
                if 'price' in tx and 'quantity' in tx:
                    amount = tx['price'] * tx['quantity']
                elif 'amount' in tx:
                    amount = tx['amount']
                
                if amount:
                    transaction_amounts.append(amount)
                
                # Count stocks
                if 'stockSymbol' in tx and tx['stockSymbol']:
                    stock = tx['stockSymbol']
                    if stock in stock_counts:
                        stock_counts[stock] += 1
                    else:
                        stock_counts[stock] = 1
            
            # Find most active day
            most_active_day = None
            most_active_count = 0
            total_transactions = sum(day_counts.values())
            
            if total_transactions > 0:
                for day, count in day_counts.items():
                    if count > most_active_count:
                        most_active_day = day
                        most_active_count = count
                
                # Calculate percentage
                day_percentage = (most_active_count / total_transactions) * 100 if total_transactions > 0 else 0
                
                # Add most active day metric
                metrics.append({
                    "label": "Most Active Day",
                    "value": day_names.get(most_active_day, "N/A"),
                    "detail": f"{day_percentage:.0f}% of transactions" if most_active_day is not None else "Insufficient data",
                    "color": ColorPalette.ACCENT_PRIMARY
                })
            else:
                # Fallback if no transaction dates
                metrics.append({
                    "label": "Most Active Day",
                    "value": "N/A",
                    "detail": "Insufficient data",
                    "color": ColorPalette.ACCENT_PRIMARY
                })
            
            # Calculate average transaction amount
            avg_transaction = 0
            if transaction_amounts:
                avg_transaction = sum(transaction_amounts) / len(transaction_amounts)
                
                metrics.append({
                    "label": "Average Transaction",
                    "value": f"${avg_transaction:.2f}",
                    "detail": f"From {len(transaction_amounts)} transactions",
                    "color": ColorPalette.ACCENT_SUCCESS
                })
            else:
                metrics.append({
                    "label": "Average Transaction",
                    "value": "N/A",
                    "detail": "No transaction data",
                    "color": ColorPalette.ACCENT_SUCCESS
                })
            
            # Find most traded stock
            most_traded_stock = None
            most_traded_count = 0
            
            for stock, count in stock_counts.items():
                if count > most_traded_count:
                    most_traded_stock = stock
                    most_traded_count = count
            
            if most_traded_stock:
                # Get stock name if available
                stock_name = most_traded_stock
                if self.stocks_the_user_has and most_traded_stock in self.stocks_the_user_has:
                    stock_name = self.stocks_the_user_has[most_traded_stock].get('name', most_traded_stock)
                
                metrics.append({
                    "label": "Most Traded Stock",
                    "value": most_traded_stock,
                    "detail": f"{most_traded_count} trades",
                    "color": ColorPalette.ACCENT_INFO
                })
            else:
                metrics.append({
                    "label": "Most Traded Stock",
                    "value": "N/A",
                    "detail": "No stock transactions",
                    "color": ColorPalette.ACCENT_INFO
                })
            
        except Exception as e:
            print(f"Error calculating transaction metrics: {e}")
            
            # Provide fallback metrics if calculation fails
            if not metrics:
                metrics = [
                    {
                        "label": "Most Active Day",
                        "value": "N/A",
                        "detail": "Data unavailable",
                        "color": ColorPalette.ACCENT_PRIMARY
                    },
                    {
                        "label": "Average Transaction",
                        "value": "N/A",
                        "detail": "Data unavailable",
                        "color": ColorPalette.ACCENT_SUCCESS
                    },
                    {
                        "label": "Most Traded Stock",
                        "value": "N/A",
                        "detail": "Data unavailable",
                        "color": ColorPalette.ACCENT_INFO
                    }
                ]
        
        return metrics


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