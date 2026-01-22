import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from models import Customer, Booking

class Database:
    """Database handler for SQLite operations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create customers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create bookings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                booking_type TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                status TEXT DEFAULT 'confirmed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_or_create_customer(self, name: str, email: str, phone: str) -> int:
        """Get existing customer or create new one"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if customer exists
        cursor.execute(
            'SELECT customer_id FROM customers WHERE email = ?',
            (email,)
        )
        result = cursor.fetchone()
        
        if result:
            customer_id = result[0]
        else:
            # Create new customer
            cursor.execute(
                'INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)',
                (name, email, phone)
            )
            customer_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return customer_id
    
    def create_booking(self, customer_id: int, booking_type: str, 
                      date: str, time: str) -> int:
        """Create a new booking"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO bookings (customer_id, booking_type, date, time, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (customer_id, booking_type, date, time, 'confirmed'))
        
        booking_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return booking_id
    
    def get_all_bookings(self) -> List[dict]:
        """Get all bookings with customer details"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                b.id, b.booking_type, b.date, b.time, b.status, b.created_at,
                c.name, c.email, c.phone
            FROM bookings b
            JOIN customers c ON b.customer_id = c.customer_id
            ORDER BY b.created_at DESC
        ''')
        
        bookings = []
        for row in cursor.fetchall():
            bookings.append({
                'booking_id': row[0],
                'booking_type': row[1],
                'date': row[2],
                'time': row[3],
                'status': row[4],
                'created_at': row[5],
                'customer_name': row[6],
                'customer_email': row[7],
                'customer_phone': row[8]
            })
        
        conn.close()
        return bookings
    
    def search_bookings(self, search_term: str) -> List[dict]:
        """Search bookings by name, email, or date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        search_pattern = f'%{search_term}%'
        cursor.execute('''
            SELECT 
                b.id, b.booking_type, b.date, b.time, b.status, b.created_at,
                c.name, c.email, c.phone
            FROM bookings b
            JOIN customers c ON b.customer_id = c.customer_id
            WHERE c.name LIKE ? OR c.email LIKE ? OR b.date LIKE ?
            ORDER BY b.created_at DESC
        ''', (search_pattern, search_pattern, search_pattern))
        
        bookings = []
        for row in cursor.fetchall():
            bookings.append({
                'booking_id': row[0],
                'booking_type': row[1],
                'date': row[2],
                'time': row[3],
                'status': row[4],
                'created_at': row[5],
                'customer_name': row[6],
                'customer_email': row[7],
                'customer_phone': row[8]
            })
        
        conn.close()
        return bookings
    
    def get_booking_by_id(self, booking_id: int) -> Optional[dict]:
        """Get a specific booking by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                b.id, b.booking_type, b.date, b.time, b.status, b.created_at,
                c.name, c.email, c.phone
            FROM bookings b
            JOIN customers c ON b.customer_id = c.customer_id
            WHERE b.id = ?
        ''', (booking_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'booking_id': row[0],
                'booking_type': row[1],
                'date': row[2],
                'time': row[3],
                'status': row[4],
                'created_at': row[5],
                'customer_name': row[6],
                'customer_email': row[7],
                'customer_phone': row[8]
            }
        return None