import sys
import os
from datetime import datetime

from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QFrame, QHBoxLayout,
                               QLabel, QGridLayout, QScrollArea, QSizePolicy, QGraphicsDropShadowEffect,
                               QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QComboBox, 
                               QTabWidget, QStackedWidget, QBoxLayout)
from PySide6.QtGui import (QColor, QFont, QPainter, QLinearGradient, QBrush, QPen,
                           QFontMetrics, QIcon)
from PySide6.QtCore import (Qt, QSize, QRect, QTimer, QEvent)

# Import shared components from previous files
from View.shared_components import ColorPalette, GlobalStyle, AvatarWidget
from View.ai_advisor_window import AIAdvisorWindow

class PortfolioPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Header with portfolio overview
        header = self._create_portfolio_header()
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
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(20)

        # Create portfolio sections
        self._setup_portfolio_analysis_section()
        self._setup_portfolio_composition_section()
        self._setup_performance_tracking_section()

        # Set the scroll area widget
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)

        # Install event filter for responsive design
        self.installEventFilter(self)

    def _create_portfolio_header(self):
        """Create a header with portfolio summary and key actions"""
        header = QFrame()
        header.setMinimumHeight(80)
        header.setStyleSheet("background-color: transparent;")

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(20)

        # Portfolio title and summary
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)

        title = QLabel("Your Portfolio")
        title.setStyleSheet(GlobalStyle.HEADER_STYLE)

        portfolio_summary = QLabel("Comprehensive Investment Overview")
        portfolio_summary.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 14px;")

        title_layout.addWidget(title)
        title_layout.addWidget(portfolio_summary)

        # Portfolio value and key metrics
        metrics_layout = QHBoxLayout()
        metrics = [
            {"label": "Total Value", "value": "$1,234,567"},
            {"label": "Daily Change", "value": "+$4,567 (3.7%)"},
            {"label": "YTD Return", "value": "+18.5%"}
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

        # Action buttons
        action_layout = QHBoxLayout()
        action_buttons = [
            {"text": "Add Funds", "style": GlobalStyle.PRIMARY_BUTTON},
            {"text": "Withdraw", "style": GlobalStyle.SECONDARY_BUTTON}
        ]

        for btn_info in action_buttons:
            btn = QPushButton(btn_info["text"])
            btn.setStyleSheet(btn_info["style"])
            btn.setFixedHeight(40)
            action_layout.addWidget(btn)

        # Combine layouts
        header_layout.addLayout(title_layout)
        header_layout.addStretch(1)
        header_layout.addLayout(metrics_layout)
        header_layout.addLayout(action_layout)

        return header

    def _setup_portfolio_analysis_section(self):
        """Create a section for detailed portfolio analysis"""
        section = QFrame()
        section_layout = QHBoxLayout(section)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(20)

        # Asset Allocation Card
        asset_allocation = QFrame()
        asset_allocation.setStyleSheet(GlobalStyle.CARD_STYLE)
        asset_layout = QVBoxLayout(asset_allocation)
        asset_layout.setContentsMargins(20, 20, 20, 20)
        asset_layout.setSpacing(15)

        # Title
        asset_title = QLabel("Asset Allocation")
        asset_title.setStyleSheet(GlobalStyle.SUBHEADER_STYLE)
        asset_layout.addWidget(asset_title)

        # Allocation breakdown
        allocation_breakdown = QWidget()
        breakdown_layout = QGridLayout(allocation_breakdown)
        breakdown_layout.setContentsMargins(0, 0, 0, 0)
        breakdown_layout.setSpacing(10)

        allocations = [
            {"category": "Stocks", "percentage": 65, "color": ColorPalette.ACCENT_PRIMARY},
            {"category": "Bonds", "percentage": 20, "color": ColorPalette.ACCENT_SUCCESS},
            {"category": "ETFs", "percentage": 10, "color": ColorPalette.ACCENT_INFO},
            {"category": "Cash", "percentage": 5, "color": ColorPalette.ACCENT_WARNING}
        ]

        for i, alloc in enumerate(allocations):
            category_label = QLabel(alloc["category"])
            category_label.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY};")
            
            percentage_label = QLabel(f"{alloc['percentage']}%")
            percentage_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY};")
            
            progress_bar = QFrame()
            progress_bar.setStyleSheet(f"""
                background-color: {alloc['color']}30;
                border-radius: 4px;
            """)
            progress_bar.setFixedHeight(10)
            
            progress_indicator = QFrame(progress_bar)
            progress_indicator.setStyleSheet(f"""
                background-color: {alloc['color']};
                border-radius: 4px;
            """)
            progress_indicator.setGeometry(0, 0, progress_bar.width() * (alloc['percentage']/100), 10)

            breakdown_layout.addWidget(category_label, i, 0)
            breakdown_layout.addWidget(progress_bar, i, 1)
            breakdown_layout.addWidget(percentage_label, i, 2)

        asset_layout.addWidget(allocation_breakdown)

        # Risk Assessment Card
        risk_assessment = QFrame()
        risk_assessment.setStyleSheet(GlobalStyle.CARD_STYLE)
        risk_layout = QVBoxLayout(risk_assessment)
        risk_layout.setContentsMargins(20, 20, 20, 20)
        risk_layout.setSpacing(15)

        # Title
        risk_title = QLabel("Risk Assessment")
        risk_title.setStyleSheet(GlobalStyle.SUBHEADER_STYLE)
        risk_layout.addWidget(risk_title)

        # Risk level indicator
        risk_level_widget = QWidget()
        risk_level_layout = QHBoxLayout(risk_level_widget)
        risk_level_layout.setContentsMargins(0, 0, 0, 0)
        risk_level_layout.setSpacing(10)

        risk_levels = ["Low", "Medium-Low", "Medium", "Medium-High", "High"]
        for level in risk_levels:
            level_indicator = QFrame()
            level_indicator.setFixedSize(40, 10)
            level_indicator.setStyleSheet(f"""
                background-color: {ColorPalette.BORDER_LIGHT}30;
                border-radius: 4px;
            """)
            
            # Highlight current risk level
            if level == "Medium":
                level_indicator.setStyleSheet(f"""
                    background-color: {ColorPalette.ACCENT_WARNING};
                    border-radius: 4px;
                """)
            
            risk_level_layout.addWidget(level_indicator)

        risk_layout.addWidget(risk_level_widget)

        # Risk description
        risk_desc = QLabel("Your portfolio has a balanced risk profile with moderate volatility.")
        risk_desc.setStyleSheet(f"""
            color: {ColorPalette.TEXT_SECONDARY};
            font-size: 13px;
        """)
        risk_desc.setWordWrap(True)
        risk_layout.addWidget(risk_desc)

        # Add to section layout
        section_layout.addWidget(asset_allocation, 1)
        section_layout.addWidget(risk_assessment, 1)

        # Add to content layout
        self.content_layout.addWidget(section)

    def _setup_portfolio_composition_section(self):
        """Create a section for portfolio composition and performance"""
        section = QFrame()
        section_layout = QHBoxLayout(section)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(20)

        # Detailed Holdings Card
        holdings_card = QFrame()
        holdings_card.setStyleSheet(GlobalStyle.CARD_STYLE)
        holdings_layout = QVBoxLayout(holdings_card)
        holdings_layout.setContentsMargins(20, 20, 20, 20)
        holdings_layout.setSpacing(15)

        # Title and Sort
        title_layout = QHBoxLayout()
        holdings_title = QLabel("Your Holdings")
        holdings_title.setStyleSheet(GlobalStyle.SUBHEADER_STYLE)
        
        sort_combo = QComboBox()
        sort_combo.addItems(["Performance", "Alphabetical", "Position Size"])
        sort_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {ColorPalette.BG_DARK};
                color: {ColorPalette.TEXT_PRIMARY};
                border: none;
                border-radius: 6px;
                padding: 5px 10px;
            }}
        """)

        title_layout.addWidget(holdings_title)
        title_layout.addStretch()
        title_layout.addWidget(sort_combo)
        holdings_layout.addLayout(title_layout)

        # Holdings Table
        holdings_table = QTableWidget()
        holdings_table.setColumnCount(5)
        holdings_table.setHorizontalHeaderLabels(["Stock", "Shares", "Price", "Total Value", "Change"])
        holdings_table.setStyleSheet(GlobalStyle.TABLE_STYLE)
        holdings_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Sample holdings data
        holdings_data = [
            {"name": "Apple Inc.", "shares": 25, "price": "$173.45", "total": "$4,336.25", "change": "+1.2%"},
            {"name": "Microsoft Corp", "shares": 15, "price": "$324.62", "total": "$4,869.30", "change": "+0.8%"},
            {"name": "Google LLC", "shares": 10, "price": "$139.78", "total": "$1,397.80", "change": "-0.6%"},
            {"name": "Amazon.com Inc", "shares": 8, "price": "$128.91", "total": "$1,031.28", "change": "+2.3%"},
            {"name": "Tesla Inc", "shares": 20, "price": "$238.79", "total": "$4,775.80", "change": "-1.5%"}
        ]

        holdings_table.setRowCount(len(holdings_data))
        for row, holding in enumerate(holdings_data):
            # Stock name
            name_item = QTableWidgetItem(holding["name"])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)

            # Shares
            shares_item = QTableWidgetItem(str(holding["shares"]))
            shares_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            shares_item.setFlags(shares_item.flags() & ~Qt.ItemIsEditable)

            # Price
            price_item = QTableWidgetItem(holding["price"])
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            price_item.setFlags(price_item.flags() & ~Qt.ItemIsEditable)

            # Total Value
            total_item = QTableWidgetItem(holding["total"])
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            total_item.setFlags(total_item.flags() & ~Qt.ItemIsEditable)

            # Change
            change_item = QTableWidgetItem(holding["change"])
            change_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if float(holding["change"].rstrip('%')) >= 0:
                change_item.setForeground(QColor(ColorPalette.ACCENT_SUCCESS))
            else:
                change_item.setForeground(QColor(ColorPalette.ACCENT_DANGER))
            change_item.setFlags(change_item.flags() & ~Qt.ItemIsEditable)

            # Set items in the table
            holdings_table.setItem(row, 0, name_item)
            holdings_table.setItem(row, 1, shares_item)
            holdings_table.setItem(row, 2, price_item)
            holdings_table.setItem(row, 3, total_item)
            holdings_table.setItem(row, 4, change_item)

        holdings_layout.addWidget(holdings_table)

        # Actions
        action_layout = QHBoxLayout()
        action_buttons = [
            {"text": "Buy", "style": GlobalStyle.PRIMARY_BUTTON},
            {"text": "Sell", "style": GlobalStyle.SECONDARY_BUTTON}
        ]

        for btn_info in action_buttons:
            btn = QPushButton(btn_info["text"])
            btn.setStyleSheet(btn_info["style"])
            btn.setFixedHeight(36)
            action_layout.addWidget(btn)

        holdings_layout.addLayout(action_layout)

        # Performance Insights Card
        performance_card = QFrame()
        performance_card.setStyleSheet(GlobalStyle.CARD_STYLE)
        performance_layout = QVBoxLayout(performance_card)
        performance_layout.setContentsMargins(20, 20, 20, 20)
        performance_layout.setSpacing(15)

        # Title
        performance_title = QLabel("Performance Insights")
        performance_title.setStyleSheet(GlobalStyle.SUBHEADER_STYLE)
        performance_layout.addWidget(performance_title)

        # Performance Metrics
        metrics_widget = QWidget()
        metrics_layout = QGridLayout(metrics_widget)
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        metrics_layout.setSpacing(10)

        performance_metrics = [
            {"label": "Total Return", "value": "+24.5%", "color": ColorPalette.ACCENT_SUCCESS},
            {"label": "Benchmark (S&P 500)", "value": "+18.2%", "color": ColorPalette.ACCENT_INFO},
            {"label": "Dividend Yield", "value": "2.3%", "color": ColorPalette.TEXT_PRIMARY},
            {"label": "Sharpe Ratio", "value": "1.42", "color": ColorPalette.TEXT_PRIMARY}
        ]

        for i, metric in enumerate(performance_metrics):
            label = QLabel(metric["label"])
            label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY};")

            value = QLabel(metric["value"])
            value.setStyleSheet(f"""
                color: {metric['color']};
                font-weight: bold;
            """)

            metrics_layout.addWidget(label, i, 0)
            metrics_layout.addWidget(value, i, 1)

        performance_layout.addWidget(metrics_widget)

        # Historical Performance Graph Placeholder
        graph_placeholder = QFrame()
        graph_placeholder.setMinimumHeight(200)
        graph_placeholder.setStyleSheet(f"""
            background-color: {ColorPalette.CARD_BG_DARKER};
            border-radius: 8px;
        """)
        performance_layout.addWidget(graph_placeholder)

        # Add to section layout
        section_layout.addWidget(holdings_card, 2)
        section_layout.addWidget(performance_card, 1)

        # Add to content layout
        self.content_layout.addWidget(section)

    def _setup_performance_tracking_section(self):
        """Create a section for advanced performance tracking and analysis"""
        section = QFrame()
        section_layout = QHBoxLayout(section)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(20)

        # Transaction History Card
        transactions_card = QFrame()
        transactions_card.setStyleSheet(GlobalStyle.CARD_STYLE)
        transactions_layout = QVBoxLayout(transactions_card)
        transactions_layout.setContentsMargins(20, 20, 20, 20)
        transactions_layout.setSpacing(15)

        # Title and Filter
        title_layout = QHBoxLayout()
        transactions_title = QLabel("Transaction History")
        transactions_title.setStyleSheet(GlobalStyle.SUBHEADER_STYLE)

        # Time period filter
        period_combo = QComboBox()
        period_combo.addItems(["This Month", "Last 3 Months", "This Year", "All Time"])
        period_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {ColorPalette.BG_DARK};
                color: {ColorPalette.TEXT_PRIMARY};
                border: none;
                border-radius: 6px;
                padding: 5px 10px;
            }}
        """)

        title_layout.addWidget(transactions_title)
        title_layout.addStretch()
        title_layout.addWidget(period_combo)
        transactions_layout.addLayout(title_layout)

        # Transaction Table
        transactions_table = QTableWidget()
        transactions_table.setColumnCount(5)
        transactions_table.setHorizontalHeaderLabels(["Date", "Type", "Stock", "Shares", "Total Value"])
        transactions_table.setStyleSheet(GlobalStyle.TABLE_STYLE)
        transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Sample transaction data
        transactions_data = [
            {"date": "Mar 1, 2025", "type": "Buy", "stock": "Apple Inc.", "shares": 10, "value": "$1,734.50"},
            {"date": "Feb 15, 2025", "type": "Sell", "stock": "Tesla Inc", "shares": 5, "value": "$1,193.95"},
            {"date": "Feb 1, 2025", "type": "Buy", "stock": "Microsoft Corp", "shares": 8, "value": "$2,596.96"},
            {"date": "Jan 20, 2025", "type": "Dividend", "stock": "Johnson & Johnson", "shares": 0, "value": "$247.50"},
            {"date": "Jan 5, 2025", "type": "Buy", "stock": "Amazon.com Inc", "shares": 3, "value": "$384.63"}
        ]

        transactions_table.setRowCount(len(transactions_data))
        for row, transaction in enumerate(transactions_data):
            # Date
            date_item = QTableWidgetItem(transaction["date"])
            date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)

            # Type
            type_item = QTableWidgetItem(transaction["type"])
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            if transaction["type"] == "Buy":
                type_item.setForeground(QColor(ColorPalette.ACCENT_SUCCESS))
            elif transaction["type"] == "Sell":
                type_item.setForeground(QColor(ColorPalette.ACCENT_DANGER))
            else:
                type_item.setForeground(QColor(ColorPalette.ACCENT_INFO))

            # Stock
            stock_item = QTableWidgetItem(transaction["stock"])
            stock_item.setFlags(stock_item.flags() & ~Qt.ItemIsEditable)

            # Shares
            shares_item = QTableWidgetItem(str(transaction["shares"]))
            shares_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            shares_item.setFlags(shares_item.flags() & ~Qt.ItemIsEditable)

            # Total Value
            value_item = QTableWidgetItem(transaction["value"])
            value_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            value_item.setFlags(value_item.flags() & ~Qt.ItemIsEditable)

            # Set items in the table
            transactions_table.setItem(row, 0, date_item)
            transactions_table.setItem(row, 1, type_item)
            transactions_table.setItem(row, 2, stock_item)
            transactions_table.setItem(row, 3, shares_item)
            transactions_table.setItem(row, 4, value_item)

        transactions_layout.addWidget(transactions_table)

        # Tax Insights Card
        tax_card = QFrame()
        tax_card.setStyleSheet(GlobalStyle.CARD_STYLE)
        tax_layout = QVBoxLayout(tax_card)
        tax_layout.setContentsMargins(20, 20, 20, 20)
        tax_layout.setSpacing(15)

        # Title
        tax_title = QLabel("Tax Insights")
        tax_title.setStyleSheet(GlobalStyle.SUBHEADER_STYLE)
        tax_layout.addWidget(tax_title)

        # Tax Metrics
        tax_metrics_widget = QWidget()
        tax_metrics_layout = QGridLayout(tax_metrics_widget)
        tax_metrics_layout.setContentsMargins(0, 0, 0, 0)
        tax_metrics_layout.setSpacing(10)

        tax_metrics = [
            {"label": "Capital Gains", "value": "$12,456", "color": ColorPalette.ACCENT_WARNING},
            {"label": "Dividend Income", "value": "$3,245", "color": ColorPalette.ACCENT_SUCCESS},
            {"label": "Estimated Tax Liability", "value": "$4,567", "color": ColorPalette.ACCENT_DANGER},
            {"label": "Tax-Efficient Strategies", "value": "Recommended", "color": ColorPalette.ACCENT_INFO}
        ]

        for i, metric in enumerate(tax_metrics):
            label = QLabel(metric["label"])
            label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY};")

            value = QLabel(metric["value"])
            value.setStyleSheet(f"""
                color: {metric['color']};
                font-weight: bold;
            """)

            tax_metrics_layout.addWidget(label, i, 0)
            tax_metrics_layout.addWidget(value, i, 1)

        tax_layout.addWidget(tax_metrics_widget)

        # Tax Optimization Advice
        tax_advice = QLabel("Consider harvesting tax losses and maximizing retirement account contributions.")
        tax_advice.setStyleSheet(f"""
            color: {ColorPalette.TEXT_SECONDARY};
            font-size: 13px;
            border: 1px solid {ColorPalette.BORDER_DARK};
            border-radius: 6px;
            padding: 10px;
            background-color: {ColorPalette.CARD_BG_DARKER};
        """)
        tax_advice.setWordWrap(True)
        tax_layout.addWidget(tax_advice)

        # Add to section layout
        section_layout.addWidget(transactions_card, 2)
        section_layout.addWidget(tax_card, 1)

        # Add to content layout
        self.content_layout.addWidget(section)

    def eventFilter(self, obj, event):
        """Handle resize events for responsive design"""
        if obj == self and event.type() == QEvent.Resize:
            width = self.width()
            
            # Adjust layout for different screen sizes
            is_narrow = width < 900

            if is_narrow:
                # Switch to vertical layout for narrow screens
                for section in [section for section in self.findChildren(QFrame) if section.parent() == self.content_widget]:
                    layout = section.layout()
                    if layout and layout.direction() != QBoxLayout.TopToBottom:
                        layout.setDirection(QBoxLayout.TopToBottom)
            else:
                # Restore horizontal layout
                for section in [section for section in self.findChildren(QFrame) if section.parent() == self.content_widget]:
                    layout = section.layout()
                    if layout and layout.direction() != QBoxLayout.LeftToRight:
                        layout.setDirection(QBoxLayout.LeftToRight)

        return super().eventFilter(obj, event)

def main():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Portfolio")
    window.setMinimumSize(900, 650)
    layout = QVBoxLayout(window)
    portfolio_page = PortfolioPage()
    layout.addWidget(portfolio_page)

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()