import requests
import time

class AiChatModel:
    def __init__(self, api_base_url="http://localhost:5000"):
        self.api_base_url = api_base_url
    
    def send_message(self, message):
        """Send a message to the AI API and get a response"""
        print(f"Sending message to AI API: {message}")
        try:
            # API endpoint
            endpoint = f"{self.api_base_url}/api/rag/ask"
            
            # Set timeout and headers
            headers = {"Content-Type": "application/json"}
            
            # Send the request
            response = requests.post(
                endpoint, 
                json={"question": message}, 
                headers=headers,
                timeout=30  # 30 second timeout
            )
            
            # Check if successful
            if response.status_code == 200:
                return response.json()
            else:
                # Log the error details
                print(f"API Error (Status {response.status_code}): {response.text}")
                error_message = f"Error: Status code {response.status_code}"
                
                # Try to extract error details if possible
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_message = f"Error: {error_data['error']}"
                except:
                    pass
                
                return {
                    "advice": "I'm having trouble connecting to the financial data service. " +
                             "Please try again later or contact support if the issue persists."
                }
                
        except requests.exceptions.Timeout:
            print("API request timed out")
            return {
                "advice": "The request is taking longer than expected. " +
                         "Our servers might be experiencing high load. Please try again shortly."
            }
            
        except requests.exceptions.ConnectionError:
            print("API connection error")
            return {
                "advice": "I'm unable to connect to the financial data service. " +
                         "Please check your internet connection or try again later."
            }
            
        except Exception as e:
            print(f"Unexpected error during API call: {str(e)}")
            return {
                "advice": "Sorry, I encountered an unexpected error while processing your request. " +
                         "Please try again or contact support if the issue persists."
            }