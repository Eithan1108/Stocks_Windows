class ProfilePresenter:
    def __init__(self, view, model):
        self.view = view
        self.model = model
        self.view.set_presenter(self)
        
        # Connect signals first
        self.connect_signals()
        
        # Initialize the view with user data only if firebaseId is available
        if self.view.firebaseId:
            self.update_user_interface()
        else:
            print("Warning: No Firebase ID available, user data cannot be loaded")

    def connect_signals(self):
        """Connect UI signals to presenter methods"""
        add_money_btn = self.view.get_add_money_button()
        if add_money_btn:
            # Ensure the presenter is kept alive with the button
            self._add_money_btn = add_money_btn
            # Disconnect any existing connections first
            try:
                self._add_money_btn.clicked.disconnect()
            except:
                pass
            # Connect to our handler
            self._add_money_btn.clicked.connect(self.handle_add_money)
            print("Connected add money button to handle_add_money method")

    def update_user_interface(self):
        """Update the view with the latest user data"""
        if not self.view.firebaseId:
            print("No firebase ID available, cannot update user interface")
            return
            
        # Fetch the latest user data from the model
        user_data = self.model.get_user_data(self.view.firebaseId)
        balance = self.model.get_balance(self.view.firebaseId)
        
        if user_data:
            # Update user info in the view
            self.view.update_user_info(user_data)
        else:
            print("Failed to fetch user data")
            
        if balance is not None:
            # Update balance in the view
            self.view.update_balance(balance)
        else:
            print("Failed to fetch balance")

    def handle_add_money(self):
        print("Add money button clicked - handler called!")
        amount_text = self.view.get_money_amount()

        # Validate amount
        try:
            amount = float(amount_text)
            if amount <= 0:
                self.view.show_error_message("Please enter a positive amount.")
                return
        except ValueError:
            self.view.show_error_message("Please enter a valid amount.")
            return

        # Check if firebaseId is available
        if not self.view.firebaseId:
            self.view.show_error_message("User ID not available. Please log in again.")
            return
            
        # Add money to user's account
        print(f"Going to model to add money for user {self.view.firebaseId}")
        success = self.model.add_money(amount_text, self.view.firebaseId)

        if success:
            self.view.show_success_message("Money added successfully!")
            # Refresh the balance after successful transaction
            self.update_user_interface()
            # Clear the input field
            self.view.clear_money_input()
        else:
            self.view.show_error_message("Failed to add money. Please try again.")