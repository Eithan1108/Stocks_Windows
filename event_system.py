# event_system.py
from PySide6.QtCore import QObject, Signal

class EventSystem(QObject):
    """Centralized event system for app-wide events"""
    # Simple notification signals
    portfolio_updated = Signal()
    transactions_updated = Signal()
    
    # Data-carrying signals
    data_updated = Signal(object, object, object)  # (stocks, transactions, stock_details)
    
# Single instance to be used application-wide
event_system = EventSystem()