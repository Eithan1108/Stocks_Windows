from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import os
import json
from PySide6.QtCore import QObject, Signal, QThread

class GoogleAuthThread(QThread):
    """Thread to run Google authentication without blocking the UI"""
    
    def __init__(self, client_secret_file, scopes):
        super().__init__()
        self.client_secret_file = client_secret_file
        self.scopes = scopes
        self.credentials = None
        self.error = None
        self.cancelled = False  # Add the cancelled attribute
        
    def run(self):
        try:
            # Create the flow
            flow = InstalledAppFlow.from_client_secrets_file(
                self.client_secret_file,
                scopes=self.scopes
            )
                        
            # Run the flow with error handling
            try:
                self.credentials = flow.run_local_server(port=0)
                print("Auth completed successfully")
            except (SystemExit, KeyboardInterrupt):
                print("Auth was interrupted")
                self.cancelled = True
            except Exception as e:
                print(f"Auth error in run_local_server: {e}")
                self.error = str(e)
                
        except Exception as e:
            print(f"Overall auth error: {e}")
            self.error = str(e)


class GoogleAuthService(QObject):
    """Service to handle Google OAuth authentication for desktop applications"""
    auth_success = Signal(str)  # Signal emitted on successful authentication with token
    auth_failure = Signal(str)  # Signal emitted on authentication failure with error message
    
    def __init__(self, client_id, client_secret, parent=None):
        super().__init__(parent)
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_thread = None
        
        # Create client_secret.json if it doesn't exist
        self._ensure_client_secret_file()
    
    def _ensure_client_secret_file(self):
        """Create client_secret.json file if it doesn't exist"""
        if not os.path.exists("client_secret.json"):
            client_config = {
                "installed": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
                }
            }
            
            with open("client_secret.json", "w") as f:
                json.dump(client_config, f)
    
    def start_auth_flow(self):
        """Begin the Google authentication flow with a shorter timeout"""
        # Cancel any existing auth thread
        if self.auth_thread:
            try:
                self.auth_thread.terminate()
                self.auth_thread.wait(1000)
            except:
                pass
            self.auth_thread = None
        
        # Create and start the auth thread normally
        scopes = ["openid", 
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile"]
        
        self.auth_thread = GoogleAuthThread("client_secret.json", scopes)
        self.auth_thread.finished.connect(self._on_auth_thread_finished)
        self.auth_thread.start()
        
        # Set a shorter timeout - this is our fallback if auth is abandoned
        from PySide6.QtCore import QTimer
        self.auth_timeout = QTimer(self)
        self.auth_timeout.setSingleShot(True)
        self.auth_timeout.timeout.connect(self._on_auth_timeout)
        self.auth_timeout.start(10000)  # 10-second timeout

    def _on_auth_timeout(self):
        """Handle authentication timeout"""
        if self.auth_thread and self.auth_thread.isRunning():
            print("Authentication timed out")
            
            # Try to terminate the thread
            self.auth_thread.terminate()
            self.auth_thread.wait(1000)
            
            # Signal failure
            self.auth_failure.emit("Authentication timed out. Please try again.")
            
            # Clean up
            self.auth_thread = None
    

    def _on_auth_thread_finished(self):
        """Called when the authentication thread completes"""
        if not self.auth_thread:
            return
            
        if hasattr(self.auth_thread, 'cancelled') and self.auth_thread.cancelled:
            # User cancelled the authentication
            print("Google authentication was cancelled by the user")
            self.auth_failure.emit("Authentication was cancelled")
        elif hasattr(self.auth_thread, 'error') and self.auth_thread.error:
            # Authentication failed with an error
            print(f"Error during Google authentication: {self.auth_thread.error}")
            self.auth_failure.emit(self.auth_thread.error)
        elif hasattr(self.auth_thread, 'credentials') and self.auth_thread.credentials:
            # Authentication succeeded
            credentials = self.auth_thread.credentials
            if hasattr(credentials, 'id_token') and credentials.id_token:
                self.auth_success.emit(credentials.id_token)
            else:
                # If no ID token is available, try to use the access token
                self.auth_success.emit(credentials.token)
        else:
            # Something unexpected happened
            self.auth_failure.emit("Authentication failed for unknown reasons")
        
        # Clean up
        self.auth_thread.deleteLater()
        self.auth_thread = None