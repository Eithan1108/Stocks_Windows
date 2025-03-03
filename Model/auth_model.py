# Models/auth_model.py
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
        """Validate login credentials"""
        # Check if email and password are not empty
        if not email or not password:
            return False, "Email and password cannot be empty"

        # Check for valid email format
        if '@' not in email or '.' not in email:
            return False, "Invalid email format"

        # Check minimum password length
        if len(password) < 8:
            return False, "Password must be at least 8 characters"

        # Check if user exists and password matches
        if email in self.users and self.users[email]["password"] == password:
            return True, "Login successful"
        
        return False, "Invalid email or password"
    
    def validate_signup(self, name, email, password, confirm_password, terms_accepted):
        """Validate signup information"""
        # This is already well-implemented in your code - just move it here
        # Basic validation checks
        if not name:
            return False, "Name cannot be empty"

        if not email or '@' not in email:
            return False, "Invalid email address"

        if len(password) < 8:
            return False, "Password must be at least 8 characters"

        if password != confirm_password:
            return False, "Passwords do not match"

        if not terms_accepted:
            return False, "You must accept the terms and conditions"
        
        # Check if user already exists
        if email in self.users:
            return False, "User with this email already exists"
        
        # Add user to database
        self.users[email] = {
            "password": password,
            "name": name
        }
        
        return True, "Signup successful"
    
    def reset_password(self, email):
        """Handle password reset logic"""
        # This is already well-implemented in your code - just move it here
        if not email or '@' not in email:
            return False, "Invalid email address"
        
        if email not in self.users:
            return False, "No account found with this email"
        
        # In a real app, you would send a password reset email here
        return True, "Password reset link sent to your email"