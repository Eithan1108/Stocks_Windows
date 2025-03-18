# Models/auth_model.py
import requests
from datetime import timedelta, date

class AuthModel:
    def __init__(self):
        # For MVP, we'll use a simple in-memory database
        self.users = {
            "test@example.com": {
                "password": "password123",
                "name": "Test User"
            },
            "demo@stockmaster.com": {
                "password": "demo123",
                "name": "Demo User"
            }
        }

        self.api_base_url = "http://localhost:5000/api/user"
    
    def validate_login(self, email, password):
        if not email or '@' not in email:
            return False, "email", "Invalid email address"
        try:
            response = requests.post(
                "http://localhost:5000/api/user/login",
                json={
                    "email": email,
                    "password": password
                }
            )

            # Check API response (add proper status code handling)
            if response.status_code == 200:
                firebase_id = response.json()["firebaseUserId"]
                print("Firebase ID:", firebase_id)
                return True, "Login successful", firebase_id
            else:
                print("Invalid credentials")
                return False, "both", "Wrong email or password"
                
        except Exception as e:
            print(f"API request error: {e}")
            
            # Fall back to in-memory check if API fails
            if email in self.users and self.users[email]["password"] == password:
                return True, "Login successful", ""
            
            return False, "Invalid email or password", ""
    
    def validate_signup(self, name, email, password, confirm_password, terms_accepted):
        """Validate signup information"""
        if not name:
            return False, "name", "Name is required"
        if not email or '@' not in email:
            return False, "email", "Invalid email address"
        if not password:
            return False, "password", "Password is required"
        if len(password) < 6:
            return False, "password", "Password must be at least 6 characters"
        if password != confirm_password:
            return False, "confirm_password", "Passwords do not match"
        if not terms_accepted:
            return False, "terms_accepted", "You must accept the terms"
        
        print("Singup details: ", name, email, password)
        
        try:
            response = requests.post(
                "http://localhost:5000/api/user/register",
                json={
                    "username": name,
                    "email": email,
                    "password": password,
                    "profilePicture": ""
                }
            )

            if response.status_code == 200:
                firebase_id = response.json()["userId"]
                print("Firebase ID:", firebase_id)
                return True, "Signup successful", firebase_id
            else:
                return False, "both", response.text
            
        except Exception as e:
            print(f"API request error: {e}")
            
            # Fall back to in-memory check if API fails
            if email in self.users:
                return False, "all", "User already exists"
            
            # Add new user to in-memory database
            self.users[email] = {
                "password": password,
                "name": name
            }
            return True, "Signup successful", ""
    
    def login_with_google(self, id_token):
        """Authenticate with Google token"""
        try:
            print(f"Sending Google token to backend: {id_token[:20]}...")
            
            response = requests.post(
                f"{self.api_base_url}/login-google",
                json={"idToken": id_token}
            )
                        
            if response.status_code == 200:
                firebase_id = response.json()["firebaseUserId"]
                print("Firebase ID:", firebase_id)
                return True, "Google login successful", firebase_id
            else:
                error_message = response.text
                return False, "Google authentication failed", error_message
                    
        except Exception as e:
            print(f"API request error during Google login: {e}")
            return False, "Google authentication failed", str(e)

    def reset_password(self, email):
        """Handle password reset logic"""
        # This is already well-implemented in your code - just move it here
        if not email or '@' not in email:
            return False, "Invalid email address"
        
        if email not in self.users:
            return False, "No account found with this email"
        
        # In a real app, you would send a password reset email here
        return True, "Password reset link sent to your email"
    
    def get_user_info(self, user_id):
        """Get user information from the API"""
        try:
            response = requests.get(f"{self.api_base_url}/{user_id}")
            if response.status_code == 200:
                user_data = response.json()
                return user_data
            else:
                return None
        except Exception as e:
            print(f"API request error: {e}")
            return None
        
    def get_user_stocks(self, user_id):
        """Get user's stock portfolio from the API"""
        try:
            response = requests.get(f"{self.api_base_url}/{user_id}/stocks")
            if response.status_code == 200:
                stocks_data = response.json()
                return stocks_data
            else:
                return None
        except Exception as e:
            print(f"API request error: {e}")
            return None
        
    def get_user_transactions(self, user_id):
        """Get user's transaction history from the API"""
        try:
            response = requests.get(f"{self.api_base_url}/{user_id}/transactions")
            if response.status_code == 200:
                transactions_data = response.json()
                return transactions_data
            else:
                return None
        except Exception as e:
            print(f"API request error: {e}")
            return None
        
    def get_balance(self, firebaseId):
        """Get user's account balance from the API"""
        print(f"Getting balance for user with ID from model: {firebaseId}")
        try:
            response = requests.get("http://localhost:5000/api/user/balance/"+firebaseId)
            if response.status_code == 200:
                # Get the balance from {'balance': 0.0}
                return response.json()["balance"]
            else:
                print("Failed to get balance" + response.text)
                return None
        except Exception as e:
            print(f"API request error: {e}")
            return None
        
    def get_user_history(self, symbol):
        year = "1-1-2025"
        now = date.today()
        now = now.strftime("%Y-%m-%d")
        try:
            response = requests.get(f"http://localhost:5000/api/stocks/history?ticker={symbol}&startDate={year}&endDate={now}")
            if response.status_code == 200:
                data = response.json()
                print(f"API response for get_stock_history: {data}")
                return data
            else:
                print(f"Failed to get stock history. Status code: {response}")
                return None
        except Exception as e:
            print(f"Error fetching stock history: {str(e)}")
            return

    def get_stocks_user_holds(self, user_id, stocks):
        """Get user's stock holdings from the API"""
        print(f"Searching for stock: {stocks}")
        
        try:
            # Make a post request to the API with the stock name
            
            response = requests.post("http://localhost:5000/api/stocks/prices", json={"tickers": stocks})
            
            if response.status_code == 200:
                data = response.json()
                print(f"API response for get_stocks_user_holds in the model: {data}")
                return data
            else:
                print(f"Error fetching stocks: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Exception during API request: {str(e)}")
            return None
        

    def get_ai_advice(self):
        try:

            # A very long strin with mutliple lines for prompt

            prompt = "Give me daily tip"
             

            response = requests.get("http://localhost:5000/api/rag/daily-advice")
            
            if response.status_code == 200:
                data = response.json()
                print(f"API response for get_ai_advide in the model: {data}")
                return data
            else:
                print(f"Error fetching stocks: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception during API request: {str(e)}")
            return None
        

    