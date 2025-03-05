# Models/auth_model.py
import requests

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
    
    def validate_login(self, email, password):
        print("Validating login___________")
        print("Auth details: ", email, password)
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
                return True, "Login successful", ""
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
        print("Validating signup___________")
        print("Signup details: ", name, email, password, confirm_password, terms_accepted)
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

            print("Response status:", response.status_code)
            print("Response content:", response.text)

            if response.status_code == 200:
                return True, "Signup successful", ""
            else:
                return False, "both", "User already exists"
            
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
    
    def reset_password(self, email):
        """Handle password reset logic"""
        # This is already well-implemented in your code - just move it here
        if not email or '@' not in email:
            return False, "Invalid email address"
        
        if email not in self.users:
            return False, "No account found with this email"
        
        # In a real app, you would send a password reset email here
        return True, "Password reset link sent to your email"