# Put this in a file called loading_overlay.py
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, Signal, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QColor, QPainter, QPen, QBrush
from View.shared_components import ColorPalette

class SpinnerWidget(QWidget):
    """Custom spinner widget that doesn't require external GIF files"""
    
    def __init__(self, parent=None, size=40, color=None):
        super().__init__(parent)
        
        self.setFixedSize(size, size)
        self.angle = 0
        self.color = color or QColor(ColorPalette.ACCENT_PRIMARY)
        
        # Create spin animation
        self.spin_animation = QPropertyAnimation(self, b"rotation_angle")
        self.spin_animation.setDuration(1000)  # 1 second per rotation
        self.spin_animation.setStartValue(0)
        self.spin_animation.setEndValue(360)
        self.spin_animation.setLoopCount(-1)  # Loop indefinitely
        self.spin_animation.setEasingCurve(QEasingCurve.Linear)
    
    def get_rotation_angle(self):
        return self.angle
    
    def set_rotation_angle(self, angle):
        self.angle = angle
        self.update()  # Trigger a repaint
    
    # Create a Qt property for the animation
    rotation_angle = Property(float, get_rotation_angle, set_rotation_angle)
    
    def start(self):
        """Start spinner animation"""
        self.spin_animation.start()
    
    def stop(self):
        """Stop spinner animation"""
        self.spin_animation.stop()
    
    def paintEvent(self, event):
        """Override paint event to draw spinner"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Save painter state
        painter.save()
        
        # Calculate center and radius
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) // 2 - 3
        
        # Set up pen for the arc
        painter.setPen(QPen(Qt.transparent))
        
        # Draw background circle (lighter)
        painter.setBrush(QBrush(QColor(100, 100, 100, 40)))
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        # Rotate painter for spinner effect
        painter.translate(center_x, center_y)
        painter.rotate(self.angle)
        painter.translate(-center_x, -center_y)
        
        # Draw spinner arc
        pen = QPen(self.color, 3, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)
        
        # Only draw a portion of the circle
        painter.drawArc(center_x - radius, center_y - radius, radius * 2, radius * 2, 0, 270 * 16)
        
        # Restore painter state
        painter.restore()

class LoadingOverlay(QWidget):
    """
    A loading overlay that shows a spinner and message during background operations
    """
    finished = Signal()  # Signal to notify when loading is complete

    def __init__(self, parent=None, message="Please wait..."):
        super().__init__(parent)
        
        # Make the widget cover the entire parent
        self.setParent(parent)
        
        # Set up a semi-transparent background
        self.setStyleSheet(f"""
            background-color: rgba(0, 0, 0, 0.7);
            border-radius: 10px;
        """)
        
        # Initially hide the overlay
        self.hide()
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Add custom spinner
        self.spinner = SpinnerWidget(self, size=48)
        
        # Create message label
        self.message_label = QLabel(message)
        self.message_label.setStyleSheet("""
            color: white;
            font-size: 16px;
            font-weight: bold;
            margin-top: 15px;
        """)
        self.message_label.setAlignment(Qt.AlignCenter)
        
        # Add widgets to layout
        layout.addWidget(self.spinner, 0, Qt.AlignCenter)
        layout.addWidget(self.message_label, 0, Qt.AlignCenter)
    
    def start(self, message=None):
        """Start showing the loading overlay"""
        if message:
            self.message_label.setText(message)
        
        # Resize to cover parent
        if self.parent():
            self.resize(self.parent().size())
        
        # Start spinner animation
        self.spinner.start()
        
        # Show the overlay
        self.show()
        self.raise_()  # Bring to front
    
    def stop(self):
        """Stop showing the loading overlay"""
        self.spinner.stop()
        self.hide()
        self.finished.emit()  # Emit signal that loading is finished
    
    def paintEvent(self, event):
        """Override paint event to make background semi-transparent"""
        painter = QPainter(self)
        painter.setOpacity(0.7)
        painter.setBrush(QBrush(QColor(0, 0, 0, 180)))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())
        super().paintEvent(event)

    def showEvent(self, event):
        """When shown, resize to cover parent"""
        if self.parent():
            self.resize(self.parent().size())
        super().showEvent(event)
    
    # For simulating a finished operation after a delay (useful for testing)
    def simulate_operation(self, duration_ms=2000):
        """Simulate a background operation that takes duration_ms milliseconds"""
        QTimer.singleShot(duration_ms, self.stop)

# For backward compatibility
AnimatedLoadingOverlay = LoadingOverlay