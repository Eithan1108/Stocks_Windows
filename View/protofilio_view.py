import sys
import math
import random
from datetime import datetime, timedelta

from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QGridLayout,
                             QFrame, QHBoxLayout, QLabel, QScrollArea, 
                             QSizePolicy, QGraphicsDropShadowEffect, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QSpacerItem)
from PySide6.QtGui import (QColor, QFont, QIcon, QPainter, QPen, QBrush, 
                          QLinearGradient, QRadialGradient, QPainterPath)
from PySide6.QtCore import Qt, QSize, QRect, QTimer, QPointF, QEvent, QPropertyAnimation

from View.shared_components import ColorPalette, GlobalStyle, AvatarWidget

class PortfolioCard(QFrame):
    """Custom card widget with shadow effect and rounded corners"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("portfolioCard")
        self.setStyleSheet(f"""
            #portfolioCard {{
                background-color: {ColorPalette.BG_CARD};
                border-radius: 12px;
                padding: 0px;
            }}
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
        
        # Set up layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
class StockItem(QFrame):
    """Custom stock item widget matching the home page design with sell option"""
    def __init__(self, stock_data, is_last=False, parent=None):
        super().__init__(parent)
        self.stock_data = stock_data
        self.is_last = is_last
        self.sell_dialog = None
        self.presenter = None  # Reference to the presenter
        self.sell_btn = None   # Reference to the sell button
        self.quantity_spinner = None  # Reference to the quantity spinner

        # Make widget clickable
        self.setCursor(Qt.PointingHandCursor)
        
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
        
        # Connect mouse events
        self.installEventFilter(self)

    def _setup_ui(self):
        # Get stock data
        symbol = self.stock_data.get("symbol", "")
        name = self.stock_data.get("name", "")
        quantity = self.stock_data.get("quantity", 0)
        price = self.stock_data.get("price", 0)
        total_value = self.stock_data.get("value", 0)
        change = self.stock_data.get("change", 0)
        
        # Icon with stock initials
        initials = self._get_stock_initials(name)
        random_color = self._get_stock_color(symbol)  # Deterministic color based on symbol
        self.icon = AvatarWidget(initials, size=38, background_color=random_color)
        self.layout.addWidget(self.icon)

        # Stock info (name and shares)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)  # Tighter spacing

        self.name_label = QLabel(name)
        self.name_label.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold; font-size: 14px;")

        self.shares_label = QLabel(f"{quantity} shares")
        self.shares_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")

        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.shares_label)
        self.layout.addLayout(info_layout, 1)  # 1 = stretch factor

        # Price and total value in middle
        value_layout = QVBoxLayout()
        value_layout.setSpacing(2)
        value_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Price
        self.price_label = QLabel(f"${price:.2f}")
        self.price_label.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-weight: bold; font-size: 14px;")
        self.price_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Total value
        self.total_label = QLabel(f"${total_value:.2f}")
        self.total_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY}; font-size: 12px;")
        self.total_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        value_layout.addWidget(self.price_label)
        value_layout.addWidget(self.total_label)
        self.layout.addLayout(value_layout)

        # Change percentage with colored background
        change_layout = QVBoxLayout()
        change_layout.setSpacing(2)
        change_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        change_color = ColorPalette.ACCENT_SUCCESS if change >= 0 else ColorPalette.ACCENT_DANGER
        change_text = f"+{change:.2f}%" if change >= 0 else f"{change:.2f}%"

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

        # Add spacer to align change at the top-right
        change_layout.addWidget(self.change_label)
        change_layout.addStretch()
        
        self.layout.addLayout(change_layout)

    def _get_stock_initials(self, name):
        """Get initials from stock name"""
        if not name:
            return "S"
            
        parts = name.split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[1][0]}".upper()
        elif name:
            return name[0].upper()
        return "S"

    def _get_stock_color(self, symbol):
        """Get a deterministic color for a stock based on symbol"""
        # Define a list of colors from the palette to use
        colors = [
            ColorPalette.ACCENT_PRIMARY,
            ColorPalette.ACCENT_SUCCESS,
            ColorPalette.ACCENT_INFO,
            ColorPalette.ACCENT_WARNING,
            ColorPalette.ACCENT_INFO,
            ColorPalette.ACCENT_DANGER
        ]
        
        # Use the symbol to pick a consistent color
        if not symbol:
            return colors[0]
            
        # Simple hash function to get a consistent index
        index = sum(ord(c) for c in symbol) % len(colors)
        return colors[index]
    
    def eventFilter(self, obj, event):
        """Handle mouse events"""
        if obj == self:
            if event.type() == QEvent.Enter:
                # Mouse enter - highlight
                self.setStyleSheet(f"""
                    background-color: {ColorPalette.ACCENT_PRIMARY};
                    border: none;
                    
                    border-radius: 8px;
                """)
                return True
            elif event.type() == QEvent.Leave:
                # Mouse leave - restore
                self.setStyleSheet(f"""
                    background-color: transparent;
                    border: none;
                    
                """)
                return True
            elif event.type() == QEvent.MouseButtonPress:
                # Mouse click - show options
                self._show_stock_options()
                return True
        
        return super().eventFilter(obj, event)
    
    def register_presenter(self, presenter):
        """Register the presenter for this stock item"""
        self.presenter = presenter
    
    def get_sell_btn(self):
        """Return the sell button if it exists"""
        return self.sell_btn if self.sell_dialog and not self.sell_dialog.isHidden() else None
    
    def get_quantity(self):
        """Return the current quantity value if the dialog is open"""
        return self.quantity_spinner.value() if self.quantity_spinner else None
    
    def get_stock_symbol(self):
        """Return the stock symbol"""
        return self.stock_data.get("symbol", "")
        
    def _show_stock_options(self):
        """Show stock options dialog"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QSpinBox, QPushButton, QHBoxLayout
        
        # If a dialog is already open, close it
        if self.sell_dialog is not None:
            self.sell_dialog.close()
            self.sell_dialog = None
            self.sell_btn = None  # Clear reference
            self.quantity_spinner = None  # Clear reference
            return
        
        # Create dialog for stock actions
        self.sell_dialog = QDialog(self.window())
        self.sell_dialog.setWindowTitle(f"Sell {self.stock_data.get('name', 'Stock')}")
        self.sell_dialog.setMinimumWidth(300)
        self.sell_dialog.setStyleSheet(f"""
            background-color: {ColorPalette.BG_CARD};
            color: {ColorPalette.TEXT_PRIMARY};
        """)
        
        # Dialog layout - this was missing
        dialog_layout = QVBoxLayout(self.sell_dialog)
        dialog_layout.setSpacing(15)
        
        # Stock info
        info_label = QLabel(f"Stock: {self.stock_data.get('name', 'Unknown')} ({self.stock_data.get('symbol', '')})")
        info_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        price_label = QLabel(f"Current Price: ${self.stock_data.get('price', 0):.2f}")
        shares_owned = QLabel(f"Shares Owned: {self.stock_data.get('quantity', 0)}")
        total_value = QLabel(f"Total Value: ${self.stock_data.get('value', 0):.2f}")
        
        dialog_layout.addWidget(info_label)
        dialog_layout.addWidget(price_label)
        dialog_layout.addWidget(shares_owned)
        dialog_layout.addWidget(total_value)
        
        # Quantity selector
        quantity_layout = QHBoxLayout()
        quantity_label = QLabel("Quantity to Sell:")
        
        self.quantity_spinner = QSpinBox()  # Store reference
        self.quantity_spinner.setStyleSheet(f"""
            background-color: {ColorPalette.BG_DARK};
            color: {ColorPalette.TEXT_PRIMARY};
            border: 1px solid {ColorPalette.BORDER_DARK};
            border-radius: 4px;
            padding: 5px;
            font-size: 14px;
        """)
        self.quantity_spinner.setMinimum(1)
        self.quantity_spinner.setMaximum(self.stock_data.get('quantity', 1))
        self.quantity_spinner.setValue(1)
        
        quantity_layout.addWidget(quantity_label)
        quantity_layout.addWidget(self.quantity_spinner)
        dialog_layout.addLayout(quantity_layout)
        
        # Estimated proceeds
        proceeds_label = QLabel(f"Estimated Proceeds: ${self.stock_data.get('price', 0):.2f}")
        
        # Update proceeds when quantity changes
        def update_proceeds():
            price = self.stock_data.get('price', 0)
            qty = self.quantity_spinner.value()
            proceeds_label.setText(f"Estimated Proceeds: ${price * qty:.2f}")
        
        self.quantity_spinner.valueChanged.connect(update_proceeds)
        
        dialog_layout.addWidget(proceeds_label)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(GlobalStyle.SECONDARY_BUTTON)
        cancel_btn.clicked.connect(self.sell_dialog.close)
        
        # Create sell button but don't connect it
        self.sell_btn = QPushButton("Sell Now")
        self.sell_btn.setStyleSheet(GlobalStyle.PRIMARY_BUTTON)
        

        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(self.sell_btn)
        dialog_layout.addLayout(buttons_layout)

        if self.presenter:
            self.presenter.on_stock_dialog_opened(self)
        
        self.sell_dialog.setModal(True)
        self.sell_dialog.finished.connect(self._dialog_closed)
        self.sell_dialog.show()
    
    def _dialog_closed(self):
        """Handle dialog closed event"""
        if self.presenter:
            self.presenter.on_stock_dialog_closed(self)
        self.sell_dialog = None
        self.sell_btn = None
        self.quantity_spinner = None
    
    def _execute_sell(self, quantity):
        """Execute the sell order"""
        # This is where you would implement the actual selling logic
        from PySide6.QtWidgets import QMessageBox
        
        # Get stock info
        symbol = self.stock_data.get("symbol", "")
        name = self.stock_data.get("name", "")
        price = self.stock_data.get("price", 0)
        
        # Display confirmation message
        confirmation = QMessageBox(self.window())
        confirmation.setWindowTitle("Order Executed")
        confirmation.setText(f"Successfully sold {quantity} shares of {name} ({symbol}) at ${price:.2f}")
        confirmation.setIcon(QMessageBox.Information)
        confirmation.exec_()
        
        # You would update your actual portfolio data here
        # And then refresh the UI to show the updated portfolio
        
        # For demonstration, we'll just print to console
        print(f"SOLD: {quantity} shares of {symbol} at ${price:.2f}")

class StockTableWidget(QTableWidget):
    """Enhanced table widget for stocks with custom styling"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {ColorPalette.BG_CARD};
                color: {ColorPalette.TEXT_PRIMARY};
                border: none;
                border-radius: 8px;
                font-size: 14px;
                selection-background-color: {ColorPalette.BG_CARD};
                alternate-background-color: {ColorPalette.CARD_BG_DARKER};
            }}
            QHeaderView::section {{
                background-color: {ColorPalette.BG_CARD};
                color: {ColorPalette.TEXT_SECONDARY};
                font-weight: bold;
                padding: 10px;
                border: none;
                border-bottom: 1px solid {ColorPalette.BORDER_LIGHT};
            }}
            QTableWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {ColorPalette.BORDER_LIGHT};
            }}
        """)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(False)
        
        # Set custom font
        font = QFont()
        font.setPointSize(11)
        self.setFont(font)

class StocksListWidget(QScrollArea):
    """Custom scrollable list of stocks matching home page design with clickable stocks"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Container widget
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        
        # Layout for stock items
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Set the container as the scroll area widget
        self.setWidget(self.container)
        
    def set_stocks(self, stocks_data):
        """Set the stocks to display in the list"""
        # Clear existing items
        self._clear_layout()
        
        # Add stock items
        if not stocks_data:
            # Show empty state
            empty_label = QLabel("You don't have any stocks yet")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet(f"""
                color: {ColorPalette.TEXT_SECONDARY};
                font-size: 16px;
                padding: 30px;
            """)
            self.layout.addWidget(empty_label)
        else:
            # Add each stock item
            for i, stock_data in enumerate(stocks_data):
                # Use our updated StockItem class with click functionality
                item = StockItem(stock_data, is_last=(i == len(stocks_data) - 1), parent=self)
                self.layout.addWidget(item)
                
        # Add stretch to push items to the top
        self.layout.addStretch(1)
        
    def _clear_layout(self):
        """Clear all widgets from the layout"""
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


class PortfolioSummaryWidget(QFrame):
    """Widget to display portfolio summary metrics in a grid layout"""
    def __init__(self, metrics, parent=None):
        super().__init__(parent)
        self.metrics = metrics
        
        # Styling
        self.setStyleSheet(f"""
            background-color: transparent;
            border: none;
        """)
        
        # Use grid layout for proper alignment
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(30)  # Horizontal spacing between metric groups
        layout.setVerticalSpacing(5)  # Vertical spacing within metric groups
        
        # Add metrics in a grid - each metric takes a column
        for col, (title, value, subtitle, change_text, change_type) in enumerate(metrics):
            # Value (large font)
            value_label = QLabel(value)
            value_label.setStyleSheet(f"""
                color: {ColorPalette.TEXT_PRIMARY};
                font-size: 24px;
                font-weight: bold;
            """)
            layout.addWidget(value_label, 0, col, Qt.AlignLeft | Qt.AlignBottom)
            
            # Title (below value)
            title_label = QLabel(title)
            title_label.setStyleSheet(f"""
                color: {ColorPalette.TEXT_SECONDARY};
                font-size: 14px;
            """)
            layout.addWidget(title_label, 1, col, Qt.AlignLeft | Qt.AlignTop)
            
            # Change text (optional)
            if change_text:
                change_color = ColorPalette.ACCENT_SUCCESS if change_type == "positive" else ColorPalette.ACCENT_DANGER
                change_label = QLabel(change_text)
                change_label.setStyleSheet(f"""
                    color: {change_color};
                    font-size: 14px;
                """)
                layout.addWidget(change_label, 2, col, Qt.AlignLeft | Qt.AlignTop)
            
            # Subtitle (optional - for MTD, etc.)
            if subtitle:
                subtitle_label = QLabel(subtitle)
                subtitle_label.setStyleSheet(f"""
                    color: {ColorPalette.ACCENT_SUCCESS};
                    font-size: 14px;
                """)
                # Add to the right side of the change text or in its place
                if change_text:
                    layout.addWidget(subtitle_label, 2, col, Qt.AlignRight | Qt.AlignTop)
                else:
                    layout.addWidget(subtitle_label, 2, col, Qt.AlignLeft | Qt.AlignTop)

class AssetAllocationWidget(QFrame):
    """Improved asset allocation widget with proper pie chart rendering"""
    def __init__(self, allocations, parent=None):
        super().__init__(parent)
        self.allocations = allocations
        self.setMinimumHeight(300)
        self.setStyleSheet(f"""
            background-color: transparent;
            border: none;
        """)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Asset Allocation")
        title.setStyleSheet(f"""
            color: {ColorPalette.TEXT_PRIMARY};
            font-size: 18px;
            font-weight: bold;
        """)
        layout.addWidget(title)
        
        # Chart area takes most of the space
        self.chart_area = QFrame()
        self.chart_area.setMinimumHeight(200)
        self.chart_area.setStyleSheet("background: transparent;")
        layout.addWidget(self.chart_area, 1)  # 1 = stretch factor
        
        # Legend area at the bottom
        legend_frame = QFrame()
        legend_frame.setStyleSheet("background: transparent;")
        legend_layout = QVBoxLayout(legend_frame)
        legend_layout.setContentsMargins(0, 0, 0, 0)
        legend_layout.setSpacing(8)
        
        # Create legend items in a grid (2 columns)
        legend_grid = QGridLayout()
        legend_grid.setHorizontalSpacing(15)
        legend_grid.setVerticalSpacing(10)
        
        row, col = 0, 0
        max_cols = 2
        
        for sector, (percentage, color_code) in self.allocations.items():
            legend_item = self._create_legend_item(sector, percentage, color_code)
            legend_grid.addLayout(legend_item, row, col)
            
            # Move to next column or row
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        legend_layout.addLayout(legend_grid)
        layout.addWidget(legend_frame)
    
    def _create_legend_item(self, sector, percentage, color_code):
        """Create a legend item with color box and text"""
        item_layout = QHBoxLayout()
        item_layout.setSpacing(8)
        
        # Color indicator
        color = self._get_color_from_code(color_code)
        color_box = QFrame()
        color_box.setFixedSize(12, 12)
        color_box.setStyleSheet(f"""
            background-color: {color};
            border-radius: 2px;
        """)
        
        # Label with sector name and percentage
        label = QLabel(f"{sector}: {percentage:.1f}%")
        label.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY}; font-size: 13px;")
        
        item_layout.addWidget(color_box)
        item_layout.addWidget(label)
        item_layout.addStretch()
        
        return item_layout
    
    def _get_color_from_code(self, color_code):
        """Get the actual color value from ColorPalette"""
        # First try direct attribute access
        if hasattr(ColorPalette, color_code):
            return getattr(ColorPalette, color_code)
        
        # If not found, try predefined colors or use a default
        sector_colors = {
            "Technology": ColorPalette.ACCENT_PRIMARY,
            "Finance": ColorPalette.ACCENT_SUCCESS,
            "Healthcare": ColorPalette.ACCENT_INFO,
            "Energy": ColorPalette.ACCENT_WARNING,
            "Other": ColorPalette.ACCENT_INFO
        }
        
        return sector_colors.get(color_code, ColorPalette.ACCENT_PRIMARY)
    
    def paintEvent(self, event):
        """Enhanced paint event for better pie chart rendering"""
        super().paintEvent(event)
        
        # Only draw in the chart area
        chart_area = self.chart_area.geometry()
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Define the pie chart dimensions
        center_x = chart_area.x() + chart_area.width() // 2
        center_y = chart_area.y() + chart_area.height() // 2
        radius = min(chart_area.width(), chart_area.height()) // 2 - 20
        
        # Draw pie slices
        start_angle = 0
        for sector, (percentage, color_code) in self.allocations.items():
            # Calculate angle
            angle = percentage * 3.6  # 360 degrees / 100 = 3.6 degrees per percentage point
            
            # Set color
            color = self._get_color_from_code(color_code)
            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(QPen(QColor(ColorPalette.BG_CARD), 1))
            
            # Draw pie slice
            path = QPainterPath()
            path.moveTo(center_x, center_y)
            
            # Convert degrees to radians for the arc
            start_rad = math.radians(start_angle)
            end_rad = math.radians(start_angle + angle)
            
            # Add arc to path
            path.arcTo(center_x - radius, center_y - radius, radius * 2, radius * 2, 
                      start_angle, angle)
            path.closeSubpath()
            
            painter.drawPath(path)
            
            # Update start angle for next slice
            start_angle += angle
        
        # Draw a dark circle in the center for a donut chart effect
        painter.setBrush(QBrush(QColor(ColorPalette.BG_CARD)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center_x - radius // 2, center_y - radius // 2, radius, radius)

class PerformanceChartWidget(QFrame):
    """Interactive performance chart widget"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(250)
        self.setStyleSheet(f"""
            background-color: transparent;
            border: none;
        """)
        
        # Generate sample data
        self.generate_sample_data()
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Chart area
        self.chart_area = QFrame()
        self.chart_area.setStyleSheet("background: transparent;")
        layout.addWidget(self.chart_area, 1)  # Stretch
        
        # Period selector
        period_layout = QHBoxLayout()
        period_layout.setSpacing(10)
        
        self.periods = ["1D", "1W", "1M", "3M", "YTD", "1Y", "All"]
        self.period_buttons = {}
        
        for period in self.periods:
            btn = QPushButton(period)
            btn.setFixedSize(50, 30)
            
            # Style based on selection
            if period == "1M":  # Default selected
                btn.setStyleSheet(GlobalStyle.PRIMARY_BUTTON)
                self.selected_period = period
            else:
                btn.setStyleSheet(GlobalStyle.SECONDARY_BUTTON)
            
            # Connect the button to selection handler
            btn.clicked.connect(lambda checked, p=period: self.select_period(p))
            
            period_layout.addWidget(btn)
            self.period_buttons[period] = btn
        
        period_layout.addStretch()
        layout.addLayout(period_layout)
    
    def generate_sample_data(self):
        """Generate sample performance data"""
        # Base value and ranges for different periods
        self.performance_data = {
            "1D": self._generate_points(24, 5, 2),
            "1W": self._generate_points(7, 10, 5),
            "1M": self._generate_points(30, 15, 8),
            "3M": self._generate_points(90, 20, 12),
            "YTD": self._generate_points(180, 25, 15),
            "1Y": self._generate_points(365, 30, 20),
            "All": self._generate_points(1000, 40, 25)
        }
    
    def _generate_points(self, num_points, max_change, volatility):
        """Generate realistic looking stock chart data"""
        points = []
        base_value = 100
        current = base_value
        
        # Start with base value
        points.append((0, current))
        
        # Generate data with some trends and volatility
        trend = random.uniform(-max_change, max_change)
        trend_change_chance = 0.1  # Chance to change trend direction
        
        for i in range(1, num_points):
            # Maybe change the trend
            if random.random() < trend_change_chance:
                trend = random.uniform(-max_change, max_change)
            
            # Daily change with trend influence
            change = random.uniform(-volatility, volatility) + (trend / num_points)
            
            # Apply change percentage
            current += current * (change / 100)
            
            # Ensure we don't go below a floor value
            current = max(current, base_value * 0.5)
            
            # Add point
            points.append((i, current))
        
        return points
    
    def select_period(self, period):
        """Handle period selection"""
        if period == self.selected_period:
            return
        
        # Update button styling
        self.period_buttons[self.selected_period].setStyleSheet(GlobalStyle.SECONDARY_BUTTON)
        self.period_buttons[period].setStyleSheet(GlobalStyle.PRIMARY_BUTTON)
        
        # Update selected period
        self.selected_period = period
        
        # Trigger repaint
        self.update()
    
    def paintEvent(self, event):
        """Paint the performance chart"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get chart area
        chart_rect = self.chart_area.geometry()
        
        # Get data for selected period
        data = self.performance_data.get(self.selected_period, [])
        if not data:
            return
        
        # Determine min/max values
        min_value = min(point[1] for point in data)
        max_value = max(point[1] for point in data)
        value_range = max_value - min_value
        
        # Add padding to value range
        padding = value_range * 0.1
        min_value -= padding
        max_value += padding
        value_range = max_value - min_value
        
        # Calculate scaling factors
        x_scale = chart_rect.width() / (len(data) - 1) if len(data) > 1 else 1
        y_scale = chart_rect.height() / value_range if value_range > 0 else 1
        
        # Create points for the line
        points = []
        for i, (x, y) in enumerate(data):
            px = chart_rect.x() + i * x_scale
            # Invert Y coordinates (0 at top)
            py = chart_rect.y() + chart_rect.height() - ((y - min_value) * y_scale)
            points.append(QPointF(px, py))
        
        # Create gradient for the area under the line
        gradient = QLinearGradient(
            chart_rect.x(), chart_rect.y(), 
            chart_rect.x(), chart_rect.y() + chart_rect.height()
        )
        
        # Determine if trend is positive or negative
        is_positive = data[-1][1] >= data[0][1]
        
        if is_positive:
            gradient.setColorAt(0, QColor(ColorPalette.ACCENT_SUCCESS + "40"))  # 25% opacity
            gradient.setColorAt(1, QColor(ColorPalette.ACCENT_SUCCESS + "00"))  # Transparent
            line_color = QColor(ColorPalette.ACCENT_SUCCESS)
        else:
            gradient.setColorAt(0, QColor(ColorPalette.ACCENT_DANGER + "40"))  # 25% opacity
            gradient.setColorAt(1, QColor(ColorPalette.ACCENT_DANGER + "00"))  # Transparent
            line_color = QColor(ColorPalette.ACCENT_DANGER)
        
        # Create fill path
        fill_path = QPainterPath()
        
        if points:
            fill_path.moveTo(points[0])
            for point in points[1:]:
                fill_path.lineTo(point)
                
            # Complete the path for filling
            fill_path.lineTo(chart_rect.x() + chart_rect.width(), chart_rect.y() + chart_rect.height())
            fill_path.lineTo(chart_rect.x(), chart_rect.y() + chart_rect.height())
            fill_path.closeSubpath()
            
            # Fill the area under the line
            painter.fillPath(fill_path, gradient)
            
            # Draw the line
            painter.setPen(QPen(line_color, 2))
            
            # Draw the line path
            line_path = QPainterPath()
            line_path.moveTo(points[0])
            for point in points[1:]:
                line_path.lineTo(point)
                
            painter.drawPath(line_path)

class PortfolioHeaderWidget(QFrame):
    """Custom header for portfolio page to match dashboard style"""
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(80)
        self.setStyleSheet("""
            background-color: transparent;
            border: none;
        """)
        
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(20)
        
        # Page title and welcome message
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)
        
        user_name = user.get('name', '').split()[0] if user and 'name' in user else ''
        welcome_text = f"Welcome, {user_name}" if user_name else "Welcome"
        
        welcome_label = QLabel(welcome_text)
        welcome_label.setStyleSheet(f"""
            color: {ColorPalette.TEXT_SECONDARY};
            font-size: 14px;
        """)
        
        title = QLabel("Portfolio")
        title.setStyleSheet(f"""
            color: {ColorPalette.TEXT_PRIMARY};
            font-size: 26px;
            font-weight: bold;
        """)
        
        title_layout.addWidget(welcome_label)
        title_layout.addWidget(title)
        

        
        # Combine layouts
        layout.addLayout(title_layout)
        layout.addStretch(1)


class PortfolioPage(QWidget):
    def __init__(self, user=None, user_stocks=None, stocks_the_user_has=None, balance=None, firebaseUserId=None, parent=None):
        super().__init__(parent)
        
        # Store input data
        self.user = user
        self.user_stocks = user_stocks or []
        self.stocks_the_user_has = stocks_the_user_has or {}
        self.balance = balance or 0
        self.user_transactions = []  # Placeholder for transaction history
        self.firebaseUserId = firebaseUserId
        
        # Set up basic styling
        self.setStyleSheet(f"""
            background-color: {ColorPalette.BG_DARK};
            color: {ColorPalette.TEXT_PRIMARY};
            font-family: 'Segoe UI', Arial, sans-serif;
        """)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Create header
        header = PortfolioHeaderWidget(user=self.user)
        layout.addWidget(header)
        
        # Scrollable content area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Content widget
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(20, 0, 20, 20)
        self.content_layout.setSpacing(20)
        
        # Create sections for responsive design
        self._setup_summary_section()
        self._setup_details_section()
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # Connect resize event for responsive design
        self.installEventFilter(self)

    def set_presenter(self, presenter):
        """
        Set the presenter for this view
        """
        self.presenter = presenter

    def _calculate_daily_change(self):
        """Calculate total daily change in portfolio value"""
        total_change = 0
        for stock in self.user_stocks:
            symbol = stock['stockSymbol']
            quantity = stock['quantity']
            
            if symbol in self.stocks_the_user_has:
                stock_details = self.stocks_the_user_has[symbol]
                current_price = stock_details.get('currentPrice', 0)
                previous_close = stock_details.get('previousClose', current_price * 0.99)  # Fallback
                
                total_change += (current_price - previous_close) * quantity
        
        return total_change  # Add this return statement

    def _calculate_daily_change_percent(self):
        """Calculate percentage change of portfolio"""
        total_value = self._calculate_total_portfolio_value()
        daily_change = self._calculate_daily_change()
        
        
        return (daily_change / total_value * 100) if total_value > 0 else 0
    
    def _calculate_asset_allocation(self):
        """Calculate asset allocation percentages"""
        total_value = self._calculate_total_portfolio_value()
        
        # If no stocks, return default allocation
        if not self.user_stocks or total_value == 0:
            return {
                "Stocks": (65, "ACCENT_PRIMARY"),
                "Bonds": (20, "ACCENT_SUCCESS"),
                "ETFs": (10, "ACCENT_INFO"),
                "Cash": (5, "ACCENT_WARNING")
            }
        
        # Group stocks by sector
        sector_allocation = {}
        for stock in self.user_stocks:
            symbol = stock['stockSymbol']
            quantity = stock['quantity']
            
            if symbol in self.stocks_the_user_has:
                stock_details = self.stocks_the_user_has[symbol]
                sector = stock_details.get('sector', 'Other')
                current_price = stock_details.get('currentPrice', 0)
                stock_value = current_price * quantity
                
                sector_allocation[sector] = sector_allocation.get(sector, 0) + stock_value
        
        # Convert to percentages
        color_mapping = {
            "Technology": "ACCENT_PRIMARY",
            "Finance": "ACCENT_SUCCESS", 
            "Healthcare": "ACCENT_INFO",
            "Energy": "ACCENT_WARNING",
            "Other": "ACCENT_SECONDARY"
        }
        
        result = {}
        for sector, value in sector_allocation.items():
            percentage = (value / total_value) * 100
            color = color_mapping.get(sector, "ACCENT_SECONDARY")
            result[sector] = (round(percentage, 1), color)
        
        return result
    
    def _setup_summary_section(self):
        """Setup the portfolio summary section with portfolio metrics and asset allocation"""
        section = QWidget()
        section_layout = QHBoxLayout(section)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(20)
        
        # Portfolio summary metrics
        portfolio_summary_card = PortfolioCard()
        summary_layout = portfolio_summary_card.layout
        
        # Add title
        summary_title = QLabel("Portfolio Summary")
        summary_title.setStyleSheet(f"""
            color: {ColorPalette.TEXT_PRIMARY};
            font-size: 18px;
            font-weight: bold;
        """)
        summary_layout.addWidget(summary_title)
        
        # Calculate metrics
        total_value = self._calculate_total_portfolio_value()
        daily_change = self._calculate_daily_change()
        daily_change_percent = self._calculate_daily_change_percent()
        
        # Format change indicators
        change_sign = "+" if daily_change >= 0 else ""
        change_text = f"{change_sign}${daily_change:.2f} ({change_sign}{daily_change_percent:.2f}%)"
        change_type = "positive" if daily_change >= 0 else "negative"
        
        # Define metrics to display - with proper formatting for the UI
        metrics = [
            ("Portfolio Value", f"${total_value:,.2f}", "", change_text, change_type),
            ("Cash Balance", f"${self.balance:,.2f}", "", "", ""),
            ("Annual Return", "18.5%", "+2.3% MTD", "", ""),
            ("Total Assets", f"${total_value + self.balance:,.2f}", "", "", "")
        ]
        
        # Create and add the summary metrics widget
        summary_metrics = PortfolioSummaryWidget(metrics)
        summary_layout.addWidget(summary_metrics)
        
        # Asset allocation
        asset_allocation_card = PortfolioCard()
        allocation_layout = asset_allocation_card.layout
        
        # Calculate allocation
        allocations = self._calculate_asset_allocation()
        
        # Create and add allocation widget
        allocation_widget = AssetAllocationWidget(allocations)
        allocation_layout.addWidget(allocation_widget)
        
        # Add to section layout
        section_layout.addWidget(portfolio_summary_card, 3)  # More space for metrics
        section_layout.addWidget(asset_allocation_card, 2)   # Less space for allocation
        
        self.content_layout.addWidget(section)
        
        # Store reference for responsive design
        self.summary_section = section
        self.summary_section_layout = section_layout
    
    def _setup_details_section(self):
        """Setup the details section with holdings and performance"""
        section = QWidget()
        section_layout = QHBoxLayout(section)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(20)
        
        # Holdings card
        holdings_card = self._create_portfolio_holdings_updated()
        
        # Performance history card
        performance_card = PortfolioCard()
        performance_layout = performance_card.layout
        

        

        
        # Add to section layout
        section_layout.addWidget(holdings_card, 5)      # More space for holdings
  # Less space for performance
        
        self.content_layout.addWidget(section)
        
        # Store reference for responsive design
        self.details_section = section
        self.details_section_layout = section_layout

    def _calculate_total_portfolio_value(self):
        """Calculate total current value of portfolio"""
        total = 0
        for stock in self.user_stocks:
            symbol = stock['stockSymbol']
            quantity = stock['quantity']
            
            if symbol in self.stocks_the_user_has:
                current_price = self.stocks_the_user_has[symbol].get('currentPrice', 0)
                total += current_price * quantity
        
        return total

    def update_after_transaction(self):
        """Update the view after a successful transaction"""
        # Recalculate portfolio metrics
        total_value = self._calculate_total_portfolio_value()
        daily_change = self._calculate_daily_change()
        daily_change_percent = self._calculate_daily_change_percent()
        
        # Update the portfolio summary section
        self._update_summary_section(total_value, daily_change, daily_change_percent)
        
        # Update the holdings section with the latest stock data
        self._refresh_holdings()
        
    def _update_summary_section(self, total_value, daily_change, daily_change_percent):
        """Update the summary section with new values"""
        # Find and update the PortfolioSummaryWidget
        try:
            for i in range(self.summary_section_layout.count()):
                widget = self.summary_section_layout.itemAt(i).widget()
                if isinstance(widget, PortfolioCard):
                    for j in range(widget.layout.count()):
                        item = widget.layout.itemAt(j).widget()
                        if isinstance(item, PortfolioSummaryWidget):
                            # Create updated metrics
                            change_sign = "+" if daily_change >= 0 else ""
                            change_text = f"{change_sign}${daily_change:.2f} ({change_sign}{daily_change_percent:.2f}%)"
                            change_type = "positive" if daily_change >= 0 else "negative"
                            
                            metrics = [
                                ("Portfolio Value", f"${total_value:,.2f}", "", change_text, change_type),
                                ("Cash Balance", f"${self.balance:,.2f}", "", "", ""),
                                ("Annual Return", "18.5%", "+2.3% MTD", "", ""),
                                ("Total Assets", f"${total_value + self.balance:,.2f}", "", "", "")
                            ]
                            
                            # Replace with a new widget
                            widget.layout.removeWidget(item)
                            item.deleteLater()
                            widget.layout.addWidget(PortfolioSummaryWidget(metrics))
        except (AttributeError, IndexError) as e:
            print(f"Error updating summary section: {e}")

    def _refresh_holdings(self):
        """Refresh the holdings section with updated stock data"""
        try:
            # Find the holdings card and replace it
            holdings_card = self.details_section_layout.itemAt(0).widget()
            if holdings_card:
                self.details_section_layout.removeWidget(holdings_card)
                holdings_card.deleteLater()
                
                # Create new holdings card
                new_holdings_card = self._create_portfolio_holdings_updated()
                self.details_section_layout.insertWidget(0, new_holdings_card, 3)
        except (AttributeError, IndexError) as e:
            print(f"Error refreshing holdings: {e}")

    def _create_portfolio_holdings_updated(self):
        """Create an enhanced section to display user's stock holdings with the home page design"""
        # Create a card for holdings
        holdings_card = PortfolioCard()
        holdings_layout = holdings_card.layout
        
        # Title with action button
        title_row = QHBoxLayout()
        title_row.setSpacing(10)
        
        title = QLabel("Your Stock Holdings")
        title.setStyleSheet(f"""
            color: {ColorPalette.TEXT_PRIMARY};
            font-size: 18px;
            font-weight: bold;
        """)
        title_row.addWidget(title)
        
        title_row.addStretch(1)
        
        # Add trade button
        trade_btn = QPushButton("Trade Stocks")
        trade_btn.setStyleSheet(GlobalStyle.PRIMARY_BUTTON)
        trade_btn.setFixedSize(120, 35)
        title_row.addWidget(trade_btn)
        
        holdings_layout.addLayout(title_row)
        
        # Prepare data for stock list
        stocks_data = []
        for stock in self.user_stocks:
            symbol = stock['stockSymbol']
            quantity = stock['quantity']
            
            if symbol in self.stocks_the_user_has:
                stock_details = self.stocks_the_user_has[symbol]
                name = stock_details.get('name', symbol)
                current_price = stock_details.get('currentPrice', 0)
                previous_price = stock_details.get('previousClose', current_price * 0.99)
                total_value = current_price * quantity
                
                # Calculate daily change
                daily_change = ((current_price - previous_price) / previous_price) * 100
                
                stocks_data.append({
                    "symbol": symbol,
                    "name": name,
                    "quantity": quantity,
                    "price": current_price,
                    "value": total_value,
                    "change": daily_change
                })
        
        # Create and add the stock list widget
        stock_list = StocksListWidget()
        stock_list.set_stocks(stocks_data)
        
        # Set a reasonable height - not too large when we have few stocks
        min_height = 180
        ideal_height = min(350, max(min_height, len(stocks_data) * 65 + 20))
        stock_list.setMinimumHeight(ideal_height)
        stock_list.setMaximumHeight(ideal_height)
        
        holdings_layout.addWidget(stock_list)
        
        # Action row at the bottom
        action_row = QHBoxLayout()
        action_row.setSpacing(10)
        

        
        export_btn = QPushButton("Export to csv")
        export_btn.setStyleSheet(GlobalStyle.SECONDARY_BUTTON)
        export_btn.setFixedHeight(35)

        export_btn.clicked.connect(self._export_portfolio_to_csv)
        

        action_row.addStretch(1)
        action_row.addWidget(export_btn)
        
        holdings_layout.addLayout(action_row)

        
        return holdings_card
    

    def _export_portfolio_to_csv(self):
        """Export portfolio data to a CSV file"""
        from PySide6.QtWidgets import QFileDialog
        import csv
        from datetime import datetime
        
        # Get save location from user
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Export Portfolio Data",
            f"portfolio_export_{datetime.now().strftime('%Y%m%d')}.csv",
            "CSV Files (*.csv)"
        )
        
        # If user cancels, return
        if not file_name:
            return
        
        try:
            # Prepare data for export
            rows = []
            
            # Add header row
            rows.append([
                "Symbol", 
                "Name", 
                "Quantity", 
                "Current Price ($)", 
                "Total Value ($)", 
                "Daily Change (%)",
                "Sector"
            ])
            
            # Add data rows
            for stock in self.user_stocks:
                symbol = stock['stockSymbol']
                quantity = stock['quantity']
                
                if symbol in self.stocks_the_user_has:
                    stock_details = self.stocks_the_user_has[symbol]
                    name = stock_details.get('name', symbol)
                    current_price = stock_details.get('currentPrice', 0)
                    previous_price = stock_details.get('previousClose', current_price * 0.99)
                    total_value = current_price * quantity
                    sector = stock_details.get('sector', 'N/A')
                    
                    # Calculate daily change
                    daily_change = ((current_price - previous_price) / previous_price) * 100
                    
                    rows.append([
                        symbol,
                        name,
                        quantity,
                        f"{current_price:.2f}",
                        f"{total_value:.2f}",
                        f"{daily_change:.2f}",
                        sector
                    ])
            
            # Add summary row
            total_portfolio_value = self._calculate_total_portfolio_value()
            rows.append([])  # Empty row for separation
            rows.append([
                "TOTAL",
                "",
                "",
                "",
                f"{total_portfolio_value:.2f}",
                "",
                ""
            ])
            
            # Add cash balance
            rows.append([
                "CASH",
                "Cash Balance",
                "",
                "",
                f"{self.balance:.2f}",
                "",
                ""
            ])
            
            # Add total assets
            rows.append([
                "TOTAL ASSETS",
                "",
                "",
                "",
                f"{total_portfolio_value + self.balance:.2f}",
                "",
                ""
            ])
            
            # Add export timestamp
            rows.append([])  # Empty row for separation
            rows.append([f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
            
            # Write to CSV file
            with open(file_name, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(rows)
                
            # Show success message
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Export Successful",
                f"Portfolio data has been exported to:\n{file_name}"
            )
            
        except Exception as e:
            # Show error message
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Export Failed",
                f"An error occurred while exporting the data:\n{str(e)}"
            )

    def _connect_button_actions(self):
        """Connect button actions in the portfolio page"""
        # Find the export button in the holdings card
        for i in range(self.details_section_layout.count()):
            widget = self.details_section_layout.itemAt(i).widget()
            if isinstance(widget, PortfolioCard):
                # Look through the layouts in the card
                for j in range(widget.layout.count()):
                    item = widget.layout.itemAt(j)
                    # Check if it's a layout
                    if item and not item.widget():
                        layout = item.layout()
                        if layout:
                            # Look for the export button in this layout
                            for k in range(layout.count()):
                                btn = layout.itemAt(k).widget()
                                if isinstance(btn, QPushButton) and btn.text() == "Export Data":
                                    # Connect the export button
                                    btn.clicked.connect(self._export_portfolio_to_csv)