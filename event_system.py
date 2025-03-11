# Create a new file: event_system.py
from PySide6.QtCore import QObject, Signal

class EventSystem(QObject):
    """Centralized event system that doesn't expose model details"""
    portfolio_updated = Signal()  # Signal for portfolio updates
    transactions_updated = Signal()  # Signal for transaction updates
    
# Single instance to be used application-wide
event_system = EventSystem()