import re
from datetime import datetime
from typing import Optional, Dict
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(parent_dir, 'db'))

from models import BookingDetails
from config import Config

class BookingFlowManager:
    """Manages the booking flow and slot filling"""
    
    def __init__(self):
        self.booking_details = BookingDetails()
        self.awaiting_confirmation = False
    
    def reset(self):
        """Reset booking details"""
        self.booking_details = BookingDetails()
        self.awaiting_confirmation = False
    
    def extract_details_from_message(self, message: str) -> Dict:
        """Extract booking details from user message"""
        extracted = {}
        message_lower = message.lower()
        
        # Extract name (simple pattern)
        name_patterns = [
            r"my name is ([a-zA-Z\s]+)",
            r"i'm ([a-zA-Z\s]+)",
            r"i am ([a-zA-Z\s]+)",
            r"call me ([a-zA-Z\s]+)"
        ]
        for pattern in name_patterns:
            match = re.search(pattern, message_lower)
            if match:
                extracted['name'] = match.group(1).strip().title()
                break
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, message)
        if email_match:
            extracted['email'] = email_match.group(0)
        
        # Extract phone
        phone_pattern = r'\b(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
        phone_match = re.search(phone_pattern, message)
        if phone_match:
            extracted['phone'] = phone_match.group(0)
        
        # Extract date (YYYY-MM-DD format)
        date_pattern = r'\b\d{4}-\d{2}-\d{2}\b'
        date_match = re.search(date_pattern, message)
        if date_match:
            extracted['date'] = date_match.group(0)
        
        # Extract time (HH:MM format)
        time_pattern = r'\b([0-1]?[0-9]|2[0-3]):[0-5][0-9]\b'
        time_match = re.search(time_pattern, message)
        if time_match:
            extracted['time'] = time_match.group(0)
        
        # Extract booking type
        for booking_type in Config.BOOKING_TYPES:
            if booking_type.lower() in message_lower:
                extracted['booking_type'] = booking_type
                break
        
        return extracted
    
    def update_details(self, extracted: Dict):
        """Update booking details with extracted information"""
        if 'name' in extracted and not self.booking_details.name:
            self.booking_details.name = extracted['name']
        
        if 'email' in extracted and not self.booking_details.email:
            self.booking_details.email = extracted['email']
        
        if 'phone' in extracted and not self.booking_details.phone:
            self.booking_details.phone = extracted['phone']
        
        if 'booking_type' in extracted and not self.booking_details.booking_type:
            self.booking_details.booking_type = extracted['booking_type']
        
        if 'date' in extracted and not self.booking_details.date:
            self.booking_details.date = extracted['date']
        
        if 'time' in extracted and not self.booking_details.time:
            self.booking_details.time = extracted['time']
    
    def get_next_question(self) -> Optional[str]:
        """Get the next question to ask user"""
        if not self.booking_details.name:
            return "May I have your full name, please?"
        
        if not self.booking_details.email:
            return "What's your email address?"
        
        if not self.booking_details.phone:
            return "What's your phone number?"
        
        if not self.booking_details.booking_type:
            types_list = ", ".join(Config.BOOKING_TYPES)
            return f"What type of appointment would you like to book? Available types: {types_list}"
        
        if not self.booking_details.date:
            return "What date would you prefer? (Please use YYYY-MM-DD format, e.g., 2025-02-15)"
        
        if not self.booking_details.time:
            return "What time would you prefer? (Please use HH:MM format, e.g., 14:30)"
        
        return None
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_date(self, date_str: str) -> bool:
        """Validate date format and that it's not in the past"""
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            return date.date() >= datetime.now().date()
        except ValueError:
            return False
    
    def validate_time(self, time_str: str) -> bool:
        """Validate time format"""
        try:
            datetime.strptime(time_str, '%H:%M')
            return True
        except ValueError:
            return False
    
    def validate_details(self) -> tuple[bool, Optional[str]]:
        """Validate all booking details"""
        if not self.validate_email(self.booking_details.email):
            return False, "Invalid email format. Please provide a valid email address."
        
        if not self.validate_date(self.booking_details.date):
            return False, "Invalid date. Please provide a date in YYYY-MM-DD format that is today or in the future."
        
        if not self.validate_time(self.booking_details.time):
            return False, "Invalid time. Please provide time in HH:MM format (e.g., 14:30)."
        
        return True, None
    
    def get_confirmation_message(self) -> str:
        """Generate confirmation message with all details"""
        return f"""
Please confirm your booking details:

📋 **Booking Summary**
- **Name:** {self.booking_details.name}
- **Email:** {self.booking_details.email}
- **Phone:** {self.booking_details.phone}
- **Appointment Type:** {self.booking_details.booking_type}
- **Date:** {self.booking_details.date}
- **Time:** {self.booking_details.time}

Is this information correct? Please reply with 'yes' to confirm or 'no' to start over.
"""
    
    def is_confirmation_response(self, message: str) -> Optional[bool]:
        """Check if message is a confirmation response"""
        message_lower = message.lower().strip()
        
        positive_responses = ['yes', 'yeah', 'yep', 'confirm', 'correct', 'ok', 'okay', 'sure']
        negative_responses = ['no', 'nope', 'wrong', 'incorrect', 'cancel']
        
        if any(word in message_lower for word in positive_responses):
            return True
        elif any(word in message_lower for word in negative_responses):
            return False
        
        return None