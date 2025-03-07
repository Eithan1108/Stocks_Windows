import sys
import os
from datetime import datetime

from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QFrame, QHBoxLayout,
                               QLabel, QGridLayout, QScrollArea, QSizePolicy, QGraphicsDropShadowEffect,
                               QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QComboBox, 
                               QTabWidget, QStackedWidget, QBoxLayout, QProgressBar, QToolButton,
                               QSpacerItem)
from PySide6.QtGui import (QColor, QFont, QPainter, QLinearGradient, QBrush, QPen,
                           QFontMetrics, QIcon, QPixmap, QCursor, QRadialGradient, QPainterPath)
from PySide6.QtCore import (Qt, QSize, QRect, QTimer, QEvent, QPoint, QPointF, 
                            QPropertyAnimation, Signal)

# Import shared components from previous files
from View.shared_components import ColorPalette, GlobalStyle, AvatarWidget
from View.ai_advisor_window import AIAdvisorWindow

class PortfolioPage(QWidget):
    """Portfolio page that exactly matches the main window styling"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Set the same background color as main window
        self.setStyleSheet(f"background-color: {ColorPalette.BG_DARK};")
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Header with portfolio overview
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
        
        # Create portfolio sections
        self._setup_portfolio_summary_section()
        self._setup_portfolio_analysis_section()
        self._setup_portfolio_holdings_section()
        
        # Set the scroll area widget
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)
        
        # Install event filter for responsive design
        self.installEventFilter(self)
    
    def _create_header(self):
        """Create a header with portfolio summary and key actions"""
        header = QFrame()
        header.setMinimumHeight(80)
        header.setStyleSheet("background-color: transparent;")
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)
        header_layout.setSpacing(20)
        
        # Portfolio title and summary - exact match to Header class in main window
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)
        
        title = QLabel("Your Portfolio")
        title.setStyleSheet(GlobalStyle.HEADER_STYLE)
        
        portfolio_summary = QLabel("Comprehensive Investment Overview")
        portfolio_summary.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 14px;")
        
        title_layout.addWidget(title)
        title_layout.addWidget(portfolio_summary)
        
        # Portfolio value and key metrics - styled the same as main window
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(20)
        
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
        
        # Action buttons - same style as main window
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        
        add_btn = QPushButton("Add Funds")
        add_btn.setStyleSheet(GlobalStyle.PRIMARY_BUTTON)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFixedHeight(40)
        
        withdraw_btn = QPushButton("Withdraw")
        withdraw_btn.setStyleSheet(GlobalStyle.SECONDARY_BUTTON)
        withdraw_btn.setCursor(Qt.PointingHandCursor)
        withdraw_btn.setFixedHeight(40)
        
        action_layout.addWidget(add_btn)
        action_layout.addWidget(withdraw_btn)
        
        # Combine layouts
        header_layout.addLayout(title_layout)
        header_layout.addStretch(1)
        header_layout.addLayout(metrics_layout)
        header_layout.addLayout(action_layout)
        
        return header
    
    def _setup_portfolio_summary_section(self):
        """Portfolio summary with visual chart - exact same as PortfolioSummaryCard in main window"""
        # Create a Card that matches PortfolioSummaryCard from main window
        summary_card = QFrame()
        summary_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        summary_card.setMinimumHeight(200)
        summary_card.setMaximumHeight(250)
        
        # Get gradient colors for orange theme (same as in main window)
        color_start = "#F59E0B"  # Orange start
        color_end = "#D97706"    # Darker orange end
        
        # Update the style with gradient background - exact match
        summary_card.setStyleSheet(f"""
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                stop:0 {color_start}, stop:1 {color_end});
            border-radius: 12px;
            border: none;
        """)
        
        # Shadow effect - exact match to main window
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))  # More subtle shadow
        shadow.setOffset(0, 4)
        summary_card.setGraphicsEffect(shadow)
        
        # Card layout
        card_layout = QVBoxLayout(summary_card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)
        
        # Top section with value and change
        top_section = QHBoxLayout()
        top_section.setSpacing(15)
        
        # Value/Change section (left) - exact match to main window
        value_section = QVBoxLayout()
        value_section.setSpacing(5)
        
        # Title - same transparency and styling
        title_label = QLabel("Portfolio Value")
        title_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.8);
            font-size: 16px;
            font-weight: normal;
            background: transparent;
        """)
        
        # Balance value - large and prominent, exact match
        balance_label = QLabel("$1,234,567.89")
        balance_label.setStyleSheet("""
            color: white;
            font-size: 36px;
            font-weight: bold;
            background: transparent;
        """)
        
        # Change percentage with background - same styling
        change_label = QLabel("+4.5%")
        change_label.setStyleSheet("""
            color: white;
            font-size: 16px;
            font-weight: bold;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
            padding: 4px 10px;
        """)
        
        value_section.addWidget(title_label)
        value_section.addWidget(balance_label)
        value_section.addWidget(change_label)
        value_section.setAlignment(change_label, Qt.AlignLeft)
        
        # Time filter section (right) - matches main window
        time_filter = QHBoxLayout()
        time_periods = ["1D", "1W", "1M", "3M", "1Y", "ALL"]
        
        for period in time_periods:
            period_btn = QPushButton(period)
            period_btn.setFixedSize(50, 30)
            period_btn.setCursor(Qt.PointingHandCursor)
            
            # Style the selected period differently - exact match
            if period == "1M":
                period_btn.setStyleSheet("""
                    QPushButton {
                        color: white;
                        background-color: rgba(255, 255, 255, 0.3);
                        border: none;
                        border-radius: 6px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: rgba(255, 255, 255, 0.4);
                    }
                """)
            else:
                period_btn.setStyleSheet("""
                    QPushButton {
                        color: rgba(255, 255, 255, 0.7);
                        background-color: transparent;
                        border: none;
                        border-radius: 6px;
                    }
                    QPushButton:hover {
                        background-color: rgba(255, 255, 255, 0.2);
                    }
                """)
            
            time_filter.addWidget(period_btn)
        
        # Additional metrics in clean boxes - same as main window
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(10)
        
        metrics = [
            {"label": "Daily Change", "value": "+$12,345.67"},
            {"label": "YTD Return", "value": "+18.7%"}
        ]
        
        for metric in metrics:
            metric_frame = QFrame()
            metric_frame.setStyleSheet("""
                background-color: rgba(255, 255, 255, 0.15);
                border-radius: 8px;
            """)
            
            metric_layout = QVBoxLayout(metric_frame)
            metric_layout.setContentsMargins(15, 10, 15, 10)
            metric_layout.setSpacing(4)
            
            label = QLabel(metric["label"])
            label.setStyleSheet("""
                color: rgba(255, 255, 255, 0.7);
                font-size: 12px;
            """)
            
            value = QLabel(metric["value"])
            value.setStyleSheet("""
                color: white;
                font-size: 16px;
                font-weight: bold;
            """)
            
            metric_layout.addWidget(label)
            metric_layout.addWidget(value)
            
            metrics_layout.addWidget(metric_frame)
        
        # Combine sections
        top_right = QVBoxLayout()
        top_right.addLayout(time_filter)
        top_right.addStretch(1)
        top_right.addLayout(metrics_layout)
        
        top_section.addLayout(value_section, 1)
        top_section.addLayout(top_right, 1)
        
        # Add to card layout
        card_layout.addLayout(top_section)
        
        # Graph view - same as main window's trend data
        graph_label = QLabel()
        graph_label.setMinimumHeight(80)
        graph_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        graph_label.setStyleSheet("background: transparent;")
        
        # Create a simplified placeholder chart with same styling
        pixmap = QPixmap(700, 100)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw a trend line - same as main window
        painter.setPen(QPen(QColor(255, 255, 255, 230), 2))
        
        # Create a path with curved line going upward
        path = QPainterPath()
        path.moveTo(0, 80)
        path.cubicTo(200, 70, 400, 50, 700, 20)
        
        painter.drawPath(path)
        
        # Draw area under curve - same gradient as main window
        fillPath = QPainterPath(path)
        fillPath.lineTo(700, 100)
        fillPath.lineTo(0, 100)
        fillPath.closeSubpath()
        
        gradient = QLinearGradient(0, 0, 0, 100)
        gradient.setColorAt(0, QColor(255, 255, 255, 80))
        gradient.setColorAt(1, QColor(255, 255, 255, 0))
        painter.fillPath(fillPath, gradient)
        
        painter.end()
        graph_label.setPixmap(pixmap)
        
        card_layout.addWidget(graph_label, 1)
        
        self.content_layout.addWidget(summary_card)
    
    def _setup_portfolio_analysis_section(self):
        """Create a section for detailed portfolio analysis"""
        section = QFrame()
        section_layout = QHBoxLayout(section)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(20)
        
        # Asset Allocation Card
        asset_allocation = self._create_asset_allocation_card()
        
        # Risk Assessment Card
        risk_assessment = self._create_risk_assessment_card()
        
        # Add both cards to section layout
        section_layout.addWidget(asset_allocation, 1)
        section_layout.addWidget(risk_assessment, 1)
        
        self.content_layout.addWidget(section)
        
        # Store reference for responsive design
        self.analysis_section = section
        self.analysis_section_layout = section_layout
    
    def _create_asset_allocation_card(self):
        """Create asset allocation card with exact same style as Card in main window"""
        # Card with exact styling from main window
        card = QFrame()
        card.setStyleSheet(GlobalStyle.CARD_STYLE)
        
        # Shadow effect - exact match
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))  # More subtle shadow
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)
        
        # Layout with same margins as main window
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)
        
        # Title and filter
        header_layout = QHBoxLayout()
        
        title = QLabel("Asset Allocation")
        title.setStyleSheet(GlobalStyle.SUBHEADER_STYLE)
        
        # View selector with same styling
        view_combo = QComboBox()
        view_combo.addItems(["By Asset Class", "By Sector", "By Region"])
        view_combo.setFixedWidth(140)
        view_combo.setStyleSheet(f"""
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
        header_layout.addWidget(view_combo)
        
        card_layout.addLayout(header_layout)
        
        # Content container - same darker background as main window
        content_frame = QFrame()
        content_frame.setStyleSheet(f"""
            background-color: {ColorPalette.CARD_BG_DARKER};
            border-radius: 8px;
        """)
        
        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Pie chart with same colors as main window
        pie_chart = QLabel()
        pie_chart.setFixedSize(140, 140)
        
        # Create pie chart
        chart_pixmap = QPixmap(140, 140)
        chart_pixmap.fill(Qt.transparent)
        
        painter = QPainter(chart_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center = QPoint(70, 70)
        radius = 60
        
        # Draw pie slices with same colors as main window
        painter.setPen(Qt.NoPen)
        
        # Stocks (65%)
        painter.setBrush(QColor(ColorPalette.ACCENT_PRIMARY))
        painter.drawPie(center.x() - radius, center.y() - radius, 
                      radius * 2, radius * 2, 
                      0, int(65 * 360 * 16 / 100))
        
        # Bonds (20%)
        painter.setBrush(QColor(ColorPalette.ACCENT_SUCCESS))
        painter.drawPie(center.x() - radius, center.y() - radius, 
                      radius * 2, radius * 2, 
                      int(65 * 360 * 16 / 100), int(20 * 360 * 16 / 100))
        
        # ETFs (10%)
        painter.setBrush(QColor(ColorPalette.ACCENT_INFO))
        painter.drawPie(center.x() - radius, center.y() - radius, 
                      radius * 2, radius * 2, 
                      int(85 * 360 * 16 / 100), int(10 * 360 * 16 / 100))
        
        # Cash (5%)
        painter.setBrush(QColor(ColorPalette.ACCENT_WARNING))
        painter.drawPie(center.x() - radius, center.y() - radius, 
                      radius * 2, radius * 2, 
                      int(95 * 360 * 16 / 100), int(5 * 360 * 16 / 100))
        
        # Draw inner circle for donut effect
        painter.setBrush(QColor(ColorPalette.CARD_BG_DARKER))
        painter.drawEllipse(center, radius * 0.6, radius * 0.6)
        
        painter.end()
        pie_chart.setPixmap(chart_pixmap)
        
        # Legend with same styling as main window
        legend_layout = QVBoxLayout()
        legend_layout.setSpacing(10)
        
        allocations = [
            {"category": "Stocks", "percentage": 65, "color": ColorPalette.ACCENT_PRIMARY},
            {"category": "Bonds", "percentage": 20, "color": ColorPalette.ACCENT_SUCCESS},
            {"category": "ETFs", "percentage": 10, "color": ColorPalette.ACCENT_INFO},
            {"category": "Cash", "percentage": 5, "color": ColorPalette.ACCENT_WARNING}
        ]
        
        for alloc in allocations:
            item_layout = QHBoxLayout()
            
            # Color box - same size and style
            color_box = QFrame()
            color_box.setFixedSize(12, 12)
            color_box.setStyleSheet(f"""
                background-color: {alloc['color']};
                border-radius: 2px;
            """)
            
            # Text content with same styling
            text_layout = QVBoxLayout()
            text_layout.setSpacing(2)
            
            category = QLabel(alloc["category"])
            category.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold;")
            
            percentage = QLabel(f"{alloc['percentage']}%")
            percentage.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
            
            text_layout.addWidget(category)
            text_layout.addWidget(percentage)
            
            item_layout.addWidget(color_box)
            item_layout.addSpacing(8)
            item_layout.addLayout(text_layout)
            item_layout.addStretch()
            
            legend_layout.addLayout(item_layout)
        
        legend_layout.addStretch()
        
        content_layout.addWidget(pie_chart)
        content_layout.addLayout(legend_layout)
        
        card_layout.addWidget(content_frame)
        
        # Action button with same styling
        rebalance_btn = QPushButton("Rebalance Portfolio")
        rebalance_btn.setStyleSheet(GlobalStyle.SECONDARY_BUTTON)
        rebalance_btn.setCursor(Qt.PointingHandCursor)
        rebalance_btn.setFixedHeight(36)
        
        card_layout.addWidget(rebalance_btn)
        
        return card
    
    def _create_risk_assessment_card(self):
        """Create risk assessment card with exact same style as Card in main window"""
        # Card with exact styling
        card = QFrame()
        card.setStyleSheet(GlobalStyle.CARD_STYLE)
        
        # Shadow effect - exact match
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)
        
        # Layout with same margins
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)
        
        # Title - same styling
        title = QLabel("Risk Assessment")
        title.setStyleSheet(GlobalStyle.SUBHEADER_STYLE)
        card_layout.addWidget(title)
        
        # Content container - same darker background
        content_frame = QFrame()
        content_frame.setStyleSheet(f"""
            background-color: {ColorPalette.CARD_BG_DARKER};
            border-radius: 8px;
        """)
        
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Current risk level
        risk_level_label = QLabel("Current Risk Level")
        risk_level_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 14px;")
        
        risk_value = QLabel("Medium")
        risk_value.setStyleSheet(f"""
            color: {ColorPalette.ACCENT_WARNING};
            font-size: 24px;
            font-weight: bold;
        """)
        
        # Risk scale with same styling
        scale_layout = QHBoxLayout()
        scale_layout.setSpacing(5)
        
        risk_levels = ["Low", "Medium-Low", "Medium", "Medium-High", "High"]
        for i, level in enumerate(risk_levels):
            level_indicator = QFrame()
            level_indicator.setFixedHeight(8)
            level_indicator.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            
            # Make the current level and previous levels active - same coloring
            if i <= 2:  # Up to Medium
                level_indicator.setStyleSheet(f"""
                    background-color: {ColorPalette.ACCENT_WARNING};
                    border-radius: 4px;
                """)
            else:
                level_indicator.setStyleSheet(f"""
                    background-color: {ColorPalette.BORDER_LIGHT}30;
                    border-radius: 4px;
                """)
            
            scale_layout.addWidget(level_indicator)
        
        # Risk labels - same text style
        label_layout = QHBoxLayout()
        
        low_label = QLabel("Low Risk")
        low_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
        
        high_label = QLabel("High Risk")
        high_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
        high_label.setAlignment(Qt.AlignRight)
        
        label_layout.addWidget(low_label)
        label_layout.addStretch()
        label_layout.addWidget(high_label)
        
        # Risk description - same paragraph styling
        risk_desc = QLabel("Your portfolio has a balanced risk profile with moderate volatility. This approach balances growth potential with downside protection.")
        risk_desc.setWordWrap(True)
        risk_desc.setStyleSheet(f"""
            color: {ColorPalette.TEXT_SECONDARY};
            font-size: 13px;
            line-height: 1.4;
        """)
        
        # Add all elements to content layout
        content_layout.addWidget(risk_level_label)
        content_layout.addWidget(risk_value)
        content_layout.addSpacing(5)
        content_layout.addLayout(scale_layout)
        content_layout.addLayout(label_layout)
        content_layout.addSpacing(10)
        content_layout.addWidget(risk_desc)
        
        card_layout.addWidget(content_frame)
        
        # Action button - same styling
        adjust_btn = QPushButton("Adjust Risk Profile")
        adjust_btn.setStyleSheet(GlobalStyle.SECONDARY_BUTTON)
        adjust_btn.setCursor(Qt.PointingHandCursor)
        adjust_btn.setFixedHeight(36)
        
        card_layout.addWidget(adjust_btn)
        
        return card
    
    def _setup_portfolio_holdings_section(self):
        """Create a section for portfolio holdings and performance"""
        section = QFrame()
        section_layout = QHBoxLayout(section)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(20)
        
        # Holdings Card - exact same style as OwnedStocksWidget in main window
        holdings_card = self._create_holdings_card()
        
        # Performance Card - with same styling
        performance_card = self._create_performance_card()
        
        # Add cards to section layout
        section_layout.addWidget(holdings_card, 2)
        section_layout.addWidget(performance_card, 1)
        
        self.content_layout.addWidget(section)
        
        # Store reference for responsive design
        self.holdings_section = section
        self.holdings_section_layout = section_layout
    
    def _create_holdings_card(self):
        """Create holdings card with exact same style as OwnedStocksWidget in main window"""
        # Card with same styling
        card = QFrame()
        card.setStyleSheet(GlobalStyle.CARD_STYLE)
        
        # Shadow effect - exact match
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)
        
        # Main layout with same margins
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)
        
        # Header with title and sort option - exact match
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title - same styling
        title = QLabel("Your Portfolio")
        title.setStyleSheet(f"""
            color: {ColorPalette.TEXT_PRIMARY};
            font-size: 18px;
            font-weight: bold;
        """)
        
        # Sort dropdown - same styling
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
        
        card_layout.addLayout(header_layout)
        
        # Stocks container - same darker background
        stocks_container = QFrame()
        stocks_container.setStyleSheet(f"""
            background-color: {ColorPalette.CARD_BG_DARKER};
            border-radius: 8px;
        """)
        
        stocks_layout = QVBoxLayout(stocks_container)
        stocks_layout.setContentsMargins(0, 0, 0, 0)
        stocks_layout.setSpacing(0)  # No spacing between items - exact match to main window
        
        # Sample stock data - same as in main window
        stocks = [
            {"name": "Apple Inc.", "amount": "25", "price": "173.45", "change": 1.2},
            {"name": "Microsoft Corp", "amount": "15", "price": "324.62", "change": 0.8},
            {"name": "Google LLC", "amount": "10", "price": "139.78", "change": -0.6},
            {"name": "Amazon.com Inc", "amount": "8", "price": "128.91", "change": 2.3},
            {"name": "Tesla Inc", "amount": "20", "price": "238.79", "change": -1.5}
        ]
        
        # Create stock items - exact same style as in StockItem class from main window
        for i, stock in enumerate(stocks):
            # Create identical stock item
            item = QFrame()
            
            # Style with only bottom border when needed - exact match
            border_style = "none" if (i == len(stocks) - 1) else f"1px solid {ColorPalette.BORDER_DARK}"
            item.setStyleSheet(f"""
                background-color: transparent;
                border: none;
                border-bottom: {border_style};
            """)
            
            item.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            item.setFixedHeight(65)  # Same height as main window
            
            # Item layout - same margins
            item_layout = QHBoxLayout(item)
            item_layout.setContentsMargins(10, 8, 10, 8)
            item_layout.setSpacing(12)
            
            # Icon with company initials - same as in main window
            initials = self._get_stock_initials(stock["name"])
            color = self._get_stock_color(stock["name"])
            icon = AvatarWidget(initials, size=38, background_color=color)
            
            # Stock info - same layout and styling
            info_layout = QVBoxLayout()
            info_layout.setSpacing(2)  # Same tight spacing
            
            name_label = QLabel(stock["name"])
            name_label.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold; font-size: 14px;")
            
            shares_label = QLabel(f"{stock['amount']} shares")
            shares_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
            
            info_layout.addWidget(name_label)
            info_layout.addWidget(shares_label)
            
            # Price and change - same vertical layout
            value_layout = QVBoxLayout()
            value_layout.setSpacing(2)
            value_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Price - same styling
            price_label = QLabel(f"${stock['price']}")
            price_label.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold; font-size: 15px;")
            price_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Change with colored background - exact match
            change_value = stock["change"]
            change_color = ColorPalette.ACCENT_SUCCESS if change_value > 0 else ColorPalette.ACCENT_DANGER
            change_text = f"+{change_value}%" if change_value > 0 else f"{change_value}%"
            
            change_label = QLabel(change_text)
            change_label.setStyleSheet(f"""
                color: {change_color}; 
                font-weight: bold; 
                font-size: 13px;
                background-color: {change_color}10; 
                padding: 2px 6px; 
                border-radius: 4px;
            """)
            change_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            value_layout.addWidget(price_label)
            value_layout.addWidget(change_label)
            
            # Add components to item layout
            item_layout.addWidget(icon)
            item_layout.addLayout(info_layout, 1)  # 1 = stretch factor - same as main window
            item_layout.addLayout(value_layout)
            
            stocks_layout.addWidget(item)
        
        # Action buttons - same layout and styling as main window
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
        
        card_layout.addWidget(stocks_container)
        
        # Portfolio summary stats at the bottom - same as main window
        summary_layout = QHBoxLayout()
        summary_layout.setContentsMargins(20, 0, 20, 20)  # Bottom padding
        summary_layout.setSpacing(20)
        
        # Stats matching the main window
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
        
        card_layout.addLayout(summary_layout)
        
        return card
    
    def _create_performance_card(self):
        """Create performance card with exact same styling as Card in main window"""
        # Card with same styling
        card = QFrame()
        card.setStyleSheet(GlobalStyle.CARD_STYLE)
        
        # Shadow effect - exact match
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)
        
        # Main layout with same margins
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)
        
        # Title - same styling
        title = QLabel("Performance Insights")
        title.setStyleSheet(GlobalStyle.SUBHEADER_STYLE)
        card_layout.addWidget(title)
        
        # Content container - same darker background
        content_frame = QFrame()
        content_frame.setStyleSheet(f"""
            background-color: {ColorPalette.CARD_BG_DARKER};
            border-radius: 8px;
        """)
        
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Key metrics at the top
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(20)
        
        # Same metrics styling
        performance_metrics = [
            {"label": "Total Return", "value": "+24.5%", "color": ColorPalette.ACCENT_SUCCESS},
            {"label": "Benchmark", "value": "+18.2%", "color": ColorPalette.TEXT_PRIMARY}
        ]
        
        for metric in performance_metrics:
            metric_widget = QWidget()
            metric_layout = QVBoxLayout(metric_widget)
            metric_layout.setContentsMargins(0, 0, 0, 0)
            metric_layout.setSpacing(2)
            
            label = QLabel(metric["label"])
            label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
            
            value = QLabel(metric["value"])
            value.setStyleSheet(f"""
                color: {metric['color']};
                font-size: 18px;
                font-weight: bold;
            """)
            
            metric_layout.addWidget(label)
            metric_layout.addWidget(value)
            
            metrics_layout.addWidget(metric_widget)
        
        # Add stretch to balance layout
        metrics_layout.addStretch()
        
        content_layout.addLayout(metrics_layout)
        
        # Performance graph - with same styling
        graph_label = QLabel()
        graph_label.setMinimumHeight(150)
        graph_label.setStyleSheet("background: transparent;")
        
        # Create performance graph with same style
        pixmap = QPixmap(500, 150)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw portfolio line (better performance)
        pen = QPen(QColor(ColorPalette.ACCENT_PRIMARY))
        pen.setWidth(2)
        painter.setPen(pen)
        
        path = QPainterPath()
        path.moveTo(0, 120)
        path.cubicTo(100, 90, 250, 60, 500, 30)  # Upward curve
        
        painter.drawPath(path)
        
        # Draw benchmark line (lower performance)
        pen = QPen(QColor(ColorPalette.TEXT_SECONDARY))
        pen.setWidth(2)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        
        bench_path = QPainterPath()
        bench_path.moveTo(0, 120)
        bench_path.cubicTo(100, 100, 250, 80, 500, 60)  # Flatter curve
        
        painter.drawPath(bench_path)
        
        # Add labels
        painter.setPen(QColor(ColorPalette.TEXT_SECONDARY))
        font = QFont()
        font.setPointSize(8)
        painter.setFont(font)
        
        # X-axis labels (months)
        months = ["Mar", "Jun", "Sep", "Dec", "Mar"]
        for i, month in enumerate(months):
            x = i * (500 / (len(months) - 1))
            painter.drawText(QRect(x - 20, 135, 40, 15), Qt.AlignCenter, month)
        
        painter.end()
        graph_label.setPixmap(pixmap)
        
        content_layout.addWidget(graph_label)
        
        # Bottom metrics - same styling
        bottom_metrics = QHBoxLayout()
        
        metrics = [
            {"label": "Sharpe Ratio", "value": "1.42"},
            {"label": "Beta", "value": "0.85"},
            {"label": "Volatility", "value": "12.7%"}
        ]
        
        for metric in metrics:
            metric_widget = QWidget()
            metric_layout = QVBoxLayout(metric_widget)
            metric_layout.setContentsMargins(0, 0, 0, 0)
            metric_layout.setSpacing(2)
            
            label = QLabel(metric["label"])
            label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
            
            value = QLabel(metric["value"])
            value.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold;")
            
            metric_layout.addWidget(label)
            metric_layout.addWidget(value)
            
            bottom_metrics.addWidget(metric_widget)
            
        bottom_metrics.addStretch()
        
        content_layout.addLayout(bottom_metrics)
        
        card_layout.addWidget(content_frame)
        
        # Action button - same styling
        view_btn = QPushButton("View Detailed Report")
        view_btn.setStyleSheet(GlobalStyle.SECONDARY_BUTTON)
        view_btn.setCursor(Qt.PointingHandCursor)
        view_btn.setFixedHeight(36)
        
        card_layout.addWidget(view_btn)
        
        return card
    
    def _get_stock_initials(self, name):
        """Get initials from stock name - same as in StockItem class"""
        parts = name.split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[1][0]}".upper()
        elif name:
            return name[0].upper()
        return "S"
    
    def _get_stock_color(self, name):
        """Get a deterministic color for a stock based on name - same as StockItem class"""
        # Use the first letter to determine the color index
        if not name:
            return ColorPalette.ACCENT_PRIMARY
        
        index = ord(name[0].lower()) - ord('a')
        index = max(0, min(index, len(ColorPalette.CHART_COLORS) - 1))
        return ColorPalette.CHART_COLORS[index]
    
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
            self._adjust_section_layout(self.analysis_section_layout, is_narrow)
            self._adjust_section_layout(self.holdings_section_layout, is_narrow)
            
            # Adjust content margins - same as main window
            if is_narrow:
                self.content_layout.setContentsMargins(10, 0, 10, 10)
            else:
                self.content_layout.setContentsMargins(20, 0, 20, 20)
                
        finally:
            # Use a timer to reset the flag to prevent deadlocks - same as main window
            QTimer.singleShot(100, self._reset_adjusting_flag)
    
    def _reset_adjusting_flag(self):
        """Safely reset the adjusting flag after a delay - same as main window"""
        self._is_adjusting = False
    
    def _adjust_section_layout(self, layout, is_narrow):
        """Helper method to adjust a section layout direction - same as main window"""
        if not layout:
            return
            
        if is_narrow and layout.direction() != QBoxLayout.TopToBottom:
            layout.setDirection(QBoxLayout.TopToBottom)
        elif not is_narrow and layout.direction() != QBoxLayout.LeftToRight:
            layout.setDirection(QBoxLayout.LeftToRight)


# Main function to run the portfolio page standalone
def main():
    app = QApplication(sys.argv)
    
    # Set app style - same as main window
    app.setStyle("Fusion")
    
    # Create and show window
    window = QWidget()
    window.setWindowTitle("StockMaster Pro - Portfolio")
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
    
    portfolio_page = PortfolioPage()
    layout.addWidget(portfolio_page)
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()