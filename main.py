# main.py
import sys
from PySide6.QtWidgets import QApplication

# Import MVP components
from Model.auth_model import AuthModel
from View.auth_page import LoginWindow
from Presenter.Auth.auth_presenter import AuthPresenter

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create model, view, and presenter
    auth_model = AuthModel()
    login_window = LoginWindow()
    auth_presenter = AuthPresenter(login_window, auth_model)
    
    # Show login window
    login_window.show()
    
    sys.exit(app.exec())