from PySide6.QtCore import QObject, Signal, QThread, QCoreApplication

# Worker class that will run in a separate thread
class ApiWorker(QObject):
    finished = Signal(object)  # Signal to emit when API call completes
    error = Signal(str)        # Signal to emit on error
    
    def __init__(self, model, message):
        super().__init__()
        self.model = model
        self.message = message
    
    def run(self):
        """Run the API call in a separate thread"""
        try:
            # Get response from the model
            response = self.model.send_message(self.message)
            # Emit the finished signal with the response
            self.finished.emit(response)
        except Exception as e:
            # Emit the error signal
            self.error.emit(str(e))


class AiChatPresenter:
    def __init__(self, view, model):
        self.view = view
        self.model = model
        self.thread = None
        
        # Connect to the view's message_sent signal
        self.view.message_sent.connect(self.handle_message)
    
    def handle_message(self, message):
        """Handle a message from the view"""
        # 1. Show typing indicator
        self.view.show_typing_indicator()
        
        # 2. Force UI update
        QCoreApplication.processEvents()
        
        # 3. Create a thread for the API call
        self.thread = QThread()
        self.worker = ApiWorker(self.model, message)
        
        # 4. Move worker to thread
        self.worker.moveToThread(self.thread)
        
        # 5. Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.handle_response)
        self.worker.error.connect(self.handle_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.thread.finished.connect(self.cleanup_thread)
        
        # 6. Start the thread
        self.thread.start()
    
    def handle_response(self, response):
        """Handle successful response"""
        self.view.hide_typing_indicator()
        self.view.add_ai_response(response)
    
    def handle_error(self, error_message):
        """Handle error"""
        self.view.hide_typing_indicator()
        self.view.add_ai_response({"advice": f"Sorry, I encountered an error: {error_message}"})
    
    def cleanup_thread(self):
        """Clean up thread resources"""
        self.worker.deleteLater()
        self.thread.deleteLater()
        self.thread = None