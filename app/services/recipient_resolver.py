
from typing import List, Dict, Any
from app.api.schemas import NotificationCreate, Channel
from app.services.user_service import user_service

class RecipientResolver:
    """Resolves recipient information from various sources"""
    
    def __init__(self):
        self.user_service = user_service

    def resolve_recipients(self, request: NotificationCreate, channel: Channel) -> List[Dict[str, Any]]:
        """Resolve all recipients for the given channel"""
        recipients = []
        
        # Add recipients from user_ids
        for user_id in request.user_ids:
            user_contacts = self._get_user_contacts(user_id, channel)
            if user_contacts:
                recipients.extend(user_contacts)
        
        # Add direct email recipients
        if channel in [Channel.EMAIL, Channel.ALL] and request.emails:
            for email in request.emails:
                recipients.append({
                    'user_id': None,
                    'email': email,
                    'phone_number': None,
                    'push_token': None
                })
        
        # Add direct SMS recipients
        if channel in [Channel.SMS, Channel.ALL] and request.sms_numbers:
            for phone in request.sms_numbers:
                recipients.append({
                    'user_id': None,
                    'email': None,
                    'phone_number': phone,
                    'push_token': None
                })
        
        return recipients
    
    def _get_user_contacts(self, user_id: int, channel: Channel) -> List[Dict[str, Any]]:
        """Get user contact information from the user service"""
        user = self.user_service.get_user_by_id(user_id)
        if not user:
            return []

        contacts = []
        if channel in [Channel.EMAIL, Channel.ALL] and user.get("email"):
            contacts.append({
                'user_id': user_id,
                'email': user["email"],
                'phone_number': None,
                'push_token': None
            })
        
        if channel in [Channel.SMS, Channel.ALL] and user.get("phone_number"):
            contacts.append({
                'user_id': user_id,
                'email': None,
                'phone_number': user["phone_number"],
                'push_token': None
            })
        
        if channel in [Channel.PUSH, Channel.ALL] and user.get("push_token"):
            contacts.append({
                'user_id': user_id,
                'email': None,
                'phone_number': None,
                'push_token': user["push_token"]
            })
            
        return contacts

