from typing import Dict, Any, Optional

class UserService:
    """
    A dummy user service that provides hardcoded user data.
    In a real application, this would connect to a user database or another microservice.
    """
    def __init__(self):
        self._users: Dict[int, Dict[str, Any]] = {
            1: {
                "id": 1,
                "name": "Alice",
                "email": "alice@example.com",
                "phone_number": "+15551112222",
                "push_token": "fcm_token_alice_12345"
            },
            2: {
                "id": 2,
                "name": "Bob",
                "email": "bob@example.com",
                "phone_number": "+15553334444",
                "push_token": None  # Bob doesn't have push notifications enabled
            },
            3: {
                "id": 3,
                "name": "Charlie",
                "email": "charlie@example.com",
                "phone_number": None, # Charlie doesn't have a phone number
                "push_token": "apns_token_charlie_67890"
            },
            4: {
                "id": 4,
                "name": "David",
                "email": None, # David doesn't have an email
                "phone_number": "+15558889999",
                "push_token": "fcm_token_david_54321"
            }
        }

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves a user by their ID.
        """
        return self._users.get(user_id)

# Create a single instance of the service to be used throughout the application
user_service = UserService()
