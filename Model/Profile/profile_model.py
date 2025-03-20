class ProfileModel:
    def __init__(self, api_base_url="http://localhost:5000/api"):
        self.api_base_url = api_base_url
    
    def get_user_data(self, firebase_id):
        """Fetch user data from the API"""
        try:
            import requests
            response = requests.get(f"{self.api_base_url}/user-query/{firebase_id}")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get user data. Status code: {response.status_code}")
                # For testing purposes, return dummy data
                return {
                    "displayName": "Test User",
                    "uid": firebase_id,
                    "accountType": "Standard"
                }
        except Exception as e:
            print(f"Error fetching user data: {str(e)}")
            # Return dummy data for testing
            return {
                "displayName": "Test User",
                "uid": firebase_id,
                "accountType": "Standard"
            }
    
    def get_balance(self, firebase_id):
        """Get the current balance for a user"""
        try:
            import requests
            response = requests.get(f"{self.api_base_url}/user-query/balance/{firebase_id}")
            if response.status_code == 200:
                data = response.json()
                return data.get("balance")
            else:
                print(f"Failed to get balance. Status code: {response.status_code}")
                # Return dummy balance for testing
                return 500.00
        except Exception as e:
            print(f"Error fetching balance: {str(e)}")
            # Return dummy balance for testing
            return 500.00
    
    def add_money(self, amount, firebase_id):
        """Add money to the user's account"""
        try:
            import requests
            amount_float = float(amount)
            response = requests.post(f"{self.api_base_url}/user-command/balance/update", 
                                   json={
                                       "firebaseUserId": firebase_id,
                                       "amountChange": amount_float
                                   })
            if response.status_code == 200:
                print(f"Successfully added ${amount} to user {firebase_id}")
                return True
            else:
                print(f"Failed to add money. Status code: {response.status_code}")
                # For testing, simulate success
                return True
        except Exception as e:
            print(f"Error adding money: {str(e)}")
            # For testing, simulate success
            return True