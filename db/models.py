from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Customer:
    """Customer model"""
    customer_id: Optional[int]
    name: str
    email: str
    phone: str
    
    def to_dict(self):
        return {
            'customer_id': self.customer_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone
        }

@dataclass
class Booking:
    """Booking model"""
    id: Optional[int]
    customer_id: int
    booking_type: str
    date: str
    time: str
    status: str
    created_at: Optional[str]
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'booking_type': self.booking_type,
            'date': self.date,
            'time': self.time,
            'status': self.status,
            'created_at': self.created_at
        }

@dataclass
class BookingDetails:
    """Booking details for collection"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    booking_type: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    
    def is_complete(self) -> bool:
        """Check if all required fields are filled"""
        return all([
            self.name,
            self.email,
            self.phone,
            self.booking_type,
            self.date,
            self.time
        ])
    
    def missing_fields(self) -> list:
        """Get list of missing fields"""
        fields = []
        if not self.name:
            fields.append("name")
        if not self.email:
            fields.append("email")
        if not self.phone:
            fields.append("phone")
        if not self.booking_type:
            fields.append("booking type")
        if not self.date:
            fields.append("date")
        if not self.time:
            fields.append("time")
        return fields
    
    def to_dict(self):
        return {
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'booking_type': self.booking_type,
            'date': self.date,
            'time': self.time
        }