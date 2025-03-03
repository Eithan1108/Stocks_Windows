from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QColor, QFontDatabase
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
import sys

from shared_components import ColorPalette

class GlobalStyle:
    PRIMARY_BUTTON = f"""
        QPushButton {{
            background-color: {ColorPalette.ACCENT_PRIMARY};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background-color: {ColorPalette.ACCENT_PRIMARY}E6;
        }}
    """

    SECONDARY_BUTTON = f"""
        QPushButton {{
            background-color: {ColorPalette.CARD_BG_DARKER};
            color: {ColorPalette.TEXT_PRIMARY};
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background-color: {ColorPalette.ACCENT_PRIMARY};
            color: white;
        }}
    """

class TransactionsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("Stock Transactions")
        self.setMinimumSize(1200, 800)
        
        # Main styling
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {ColorPalette.BG_DARK};
                color: {ColorPalette.TEXT_PRIMARY};
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
            }}
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Create header with transaction actions
        self._create_header(main_layout)
        
        # Create transactions table
        self._create_transactions_table(main_layout)
        
        # Create summary section
        self._create_summary_section(main_layout)

    def _create_header(self, parent_layout):
        """Create header with title and action buttons"""
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            background-color: {ColorPalette.BG_CARD};
            border-radius: 12px;
        """)

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        header_frame.setGraphicsEffect(shadow)

        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(25, 20, 25, 20)
        header_layout.setSpacing(15)

        # Title
        title = QLabel("Transaction History")
        title.setStyleSheet(f"""
            color: {ColorPalette.TEXT_PRIMARY};
            font-size: 22px;
            font-weight: bold;
        """)

        # Action buttons
        action_layout = QHBoxLayout()
        
        # Buy button
        buy_btn = QPushButton("Buy Stocks")
        buy_btn.setStyleSheet(GlobalStyle.PRIMARY_BUTTON)
        buy_btn.setFixedHeight(40)
        
        # Sell button
        sell_btn = QPushButton("Sell Stocks")
        sell_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ColorPalette.ACCENT_DANGER};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {ColorPalette.ACCENT_DANGER}E6;
            }}
        """)
        sell_btn.setFixedHeight(40)

        # Add buttons to action layout
        action_layout.addWidget(buy_btn)
        action_layout.addWidget(sell_btn)

        # Combine title and actions
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addLayout(action_layout)

        parent_layout.addWidget(header_frame)

    def _create_transactions_table(self, parent_layout):
        """Create a comprehensive transactions table"""
        table_frame = QFrame()
        table_frame.setStyleSheet(f"""
            background-color: {ColorPalette.BG_CARD};
            border-radius: 12px;
        """)

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        table_frame.setGraphicsEffect(shadow)

        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(0, 0, 0, 0)

        # Create table
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels(["Date", "Type", "Stock", "Shares", "Price per Share", "Total Amount", "Status"])
        
        # Styling
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {ColorPalette.BG_CARD};
                color: {ColorPalette.TEXT_PRIMARY};
                alternate-background-color: {ColorPalette.CARD_BG_DARKER};
            }}
            QTableWidget::item {{
                padding: 12px;
                border: none;
                border-bottom: 1px solid {ColorPalette.BORDER_DARK};
            }}
        """)
        table.setAlternatingRowColors(True)
        table.setShowGrid(False)
        
        # Header customization
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setStyleSheet(f"""
            QHeaderView::section {{
                background-color: {ColorPalette.CARD_BG_DARKER};
                color: {ColorPalette.TEXT_PRIMARY};
                padding: 12px;
                font-weight: bold;
                border: none;
                font-size: 14px;
            }}
        """)

        # Sample transactions data
        transactions = [
            {"date": "2025-03-01", "type": "Buy", "stock": "AAPL", "shares": 10, "price": 175.32, "total": 1753.20, "status": "Completed"},
            {"date": "2025-03-05", "type": "Sell", "stock": "MSFT", "shares": 5, "price": 326.75, "total": 1633.75, "status": "Completed"},
            {"date": "2025-03-10", "type": "Buy", "stock": "GOOGL", "shares": 3, "price": 138.92, "total": 416.76, "status": "Completed"},
            {"date": "2025-03-15", "type": "Dividend", "stock": "JNJ", "shares": 0, "price": 4.50, "total": 76.50, "status": "Processed"},
            {"date": "2025-03-18", "type": "Buy", "stock": "TSLA", "shares": 2, "price": 245.30, "total": 490.60, "status": "Completed"},
            {"date": "2025-03-22", "type": "Sell", "stock": "AAPL", "shares": 5, "price": 180.45, "total": 902.25, "status": "Completed"},
            {"date": "2025-03-25", "type": "Deposit", "stock": "-", "shares": 0, "price": 0, "total": 5000.00, "status": "Completed"},
            {"date": "2025-03-28", "type": "Buy", "stock": "AMZN", "shares": 4, "price": 130.20, "total": 520.80, "status": "Completed"},
            {"date": "2025-04-02", "type": "Sell", "stock": "TSLA", "shares": 1, "price": 252.75, "total": 252.75, "status": "Completed"},
            {"date": "2025-04-05", "type": "Buy", "stock": "NVDA", "shares": 2, "price": 425.60, "total": 851.20, "status": "Completed"},
            {"date": "2025-04-10", "type": "Withdrawal", "stock": "-", "shares": 0, "price": 0, "total": 2000.00, "status": "Pending"}
        ]

        table.setRowCount(len(transactions))

        # Color mapping for different transaction types and statuses
        type_colors = {
            "Buy": ColorPalette.ACCENT_SUCCESS,
            "Sell": ColorPalette.ACCENT_DANGER,
            "Dividend": ColorPalette.ACCENT_INFO,
            "Deposit": ColorPalette.ACCENT_PRIMARY,
            "Withdrawal": ColorPalette.ACCENT_WARNING
        }

        status_colors = {
            "Completed": ColorPalette.ACCENT_SUCCESS,
            "Processed": ColorPalette.ACCENT_INFO,
            "Pending": ColorPalette.ACCENT_WARNING
        }

        for row, transaction in enumerate(transactions):
            # Date
            date_item = QTableWidgetItem(transaction["date"])
            table.setItem(row, 0, date_item)

            # Type
            type_item = QTableWidgetItem(transaction["type"])
            type_item.setForeground(QColor(type_colors.get(transaction["type"], ColorPalette.TEXT_PRIMARY)))
            table.setItem(row, 1, type_item)

            # Stock
            stock_item = QTableWidgetItem(transaction["stock"])
            table.setItem(row, 2, stock_item)

            # Shares
            shares_item = QTableWidgetItem(str(transaction["shares"]) if transaction["shares"] > 0 else "-")
            shares_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(row, 3, shares_item)

            # Price per Share
            price_item = QTableWidgetItem(f"${transaction['price']:.2f}" if transaction["price"] > 0 else "-")
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(row, 4, price_item)

            # Total Amount
            total_item = QTableWidgetItem(f"${transaction['total']:.2f}")
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Color total based on transaction type
            if transaction["type"] in ["Buy", "Withdrawal"]:
                total_item.setForeground(QColor(ColorPalette.ACCENT_DANGER))
            elif transaction["type"] in ["Sell", "Dividend", "Deposit"]:
                total_item.setForeground(QColor(ColorPalette.ACCENT_SUCCESS))
            
            table.setItem(row, 5, total_item)

            # Status
            status_item = QTableWidgetItem(transaction["status"])
            status_item.setForeground(QColor(status_colors.get(transaction["status"], ColorPalette.TEXT_PRIMARY)))
            table.setItem(row, 6, status_item)

        # Add table to layout
        table_layout.addWidget(table)

        parent_layout.addWidget(table_frame)

    def _create_summary_section(self, parent_layout):
        """Create a comprehensive summary section with detailed metrics"""
        summary_frame = QFrame()
        summary_frame.setStyleSheet(f"""
            background-color: {ColorPalette.BG_CARD};
            border-radius: 12px;
        """)

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        summary_frame.setGraphicsEffect(shadow)

        summary_layout = QHBoxLayout(summary_frame)
        summary_layout.setContentsMargins(25, 20, 25, 20)
        summary_layout.setSpacing(30)

        # Detailed summary metrics
        summary_metrics = [
            {
                "label": "Total Transactions", 
                "value": "25", 
                "color": ColorPalette.TEXT_PRIMARY
            },
            {
                "label": "Total Buy Volume", 
                "value": "$45,678.90", 
                "color": ColorPalette.ACCENT_SUCCESS
            },
            {
                "label": "Total Sell Volume", 
                "value": "$36,542.30", 
                "color": ColorPalette.ACCENT_DANGER
            },
            {
                "label": "Net Investment", 
                "value": "+$9,136.60", 
                "color": ColorPalette.ACCENT_INFO
            }
        ]

        for metric in summary_metrics:
            metric_widget = QWidget()
            metric_layout = QVBoxLayout(metric_widget)
            metric_layout.setContentsMargins(0, 0, 0, 0)
            metric_layout.setSpacing(10)

            # Label
            label = QLabel(metric["label"])
            label.setStyleSheet(f"""
                color: {ColorPalette.TEXT_SECONDARY};
                font-size: 12px;
            """)

            # Value
            value = QLabel(metric["value"])
            value.setStyleSheet(f"""
                color: {metric['color']};
                font-size: 20px;
                font-weight: bold;
            """)

            metric_layout.addWidget(label)
            metric_layout.addWidget(value)

            summary_layout.addWidget(metric_widget)

        # Add stretch to distribute metrics
        summary_layout.addStretch()

        parent_layout.addWidget(summary_frame)

def main():
    app = QApplication(sys.argv)
    
    # Optional: Set application-wide font
    font_db = QFontDatabase()
    font_db.addApplicationFont("path/to/Inter-Regular.ttf")
    font_db.addApplicationFont("path/to/Inter-Bold.ttf")
    
    window = TransactionsPage()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()