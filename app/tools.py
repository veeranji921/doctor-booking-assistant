import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
import streamlit as st
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(parent_dir, 'db'))

from config import Config
from database import Database

class RAGTool:
    """Tool for RAG-based question answering"""
    
    def __init__(self, rag_pipeline):
        self.rag_pipeline = rag_pipeline
    
    def execute(self, query: str) -> str:
        """Execute RAG query"""
        if not self.rag_pipeline.is_initialized():
            return "No documents have been uploaded yet. Please upload PDF documents first."
        
        # Retrieve relevant chunks
        chunks = self.rag_pipeline.retrieve(query)
        
        if not chunks:
            return "I couldn't find relevant information in the uploaded documents."
        
        # Format context from retrieved chunks
        context = "\n\n".join(chunks)
        return context

class BookingPersistenceTool:
    """Tool for persisting bookings to database"""
    
    def __init__(self, database: Database):
        self.database = database
    
    def execute(self, booking_data: Dict) -> Dict:
        """Save booking to database"""
        try:
            # Get or create customer
            customer_id = self.database.get_or_create_customer(
                name=booking_data['name'],
                email=booking_data['email'],
                phone=booking_data['phone']
            )
            
            # Create booking
            booking_id = self.database.create_booking(
                customer_id=customer_id,
                booking_type=booking_data['booking_type'],
                date=booking_data['date'],
                time=booking_data['time']
            )
            
            return {
                'success': True,
                'booking_id': booking_id,
                'message': f'Booking created successfully with ID: {booking_id}'
            }
        except Exception as e:
            return {
                'success': False,
                'booking_id': None,
                'message': f'Failed to create booking: {str(e)}'
            }

class EmailTool:
    """Tool for sending email confirmations"""
    
    def __init__(self):
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.email_address = Config.EMAIL_ADDRESS
        self.email_password = Config.EMAIL_PASSWORD
    
    def execute(self, to_email: str, subject: str, body: str) -> Dict:
        """Send email"""
        try:
            # Create message
            message = MIMEMultipart()
            message['From'] = self.email_address
            message['To'] = to_email
            message['Subject'] = subject
            
            # Add body
            message.attach(MIMEText(body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(message)
            
            return {
                'success': True,
                'message': 'Email sent successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to send email: {str(e)}'
            }
    
    def send_booking_confirmation(self, booking_data: Dict, booking_id: int) -> Dict:
        """Send booking confirmation email"""
        subject = f"Booking Confirmation - ID #{booking_id}"
        
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                    <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                        Appointment Confirmation
                    </h2>
                    
                    <p>Dear <strong>{booking_data['name']}</strong>,</p>
                    
                    <p>Your appointment has been successfully booked. Here are your booking details:</p>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p style="margin: 10px 0;"><strong>Booking ID:</strong> #{booking_id}</p>
                        <p style="margin: 10px 0;"><strong>Appointment Type:</strong> {booking_data['booking_type']}</p>
                        <p style="margin: 10px 0;"><strong>Date:</strong> {booking_data['date']}</p>
                        <p style="margin: 10px 0;"><strong>Time:</strong> {booking_data['time']}</p>
                        <p style="margin: 10px 0;"><strong>Contact Phone:</strong> {booking_data['phone']}</p>
                    </div>
                    
                    <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
                        <p style="margin: 0;"><strong>Important:</strong> Please arrive 10 minutes before your scheduled time.</p>
                    </div>
                    
                    <p>If you need to reschedule or cancel your appointment, please contact us as soon as possible.</p>
                    
                    <p style="margin-top: 30px;">Best regards,<br>
                    <strong>Medical Clinic Team</strong></p>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                    <p style="font-size: 12px; color: #666;">
                        This is an automated message. Please do not reply to this email.
                    </p>
                </div>
            </body>
        </html>
        """
        
        return self.execute(booking_data['email'], subject, body)

class ToolRouter:
    """Routes requests to appropriate tools"""
    
    def __init__(self, rag_pipeline, database: Database):
        self.rag_tool = RAGTool(rag_pipeline)
        self.booking_tool = BookingPersistenceTool(database)
        self.email_tool = EmailTool()
    
    def route_rag_query(self, query: str) -> str:
        """Route query to RAG tool"""
        return self.rag_tool.execute(query)
    
    def route_booking_save(self, booking_data: Dict) -> Dict:
        """Route booking save to database"""
        return self.booking_tool.execute(booking_data)
    
    def route_email_send(self, booking_data: Dict, booking_id: int) -> Dict:
        """Route email sending"""
        return self.email_tool.send_booking_confirmation(booking_data, booking_id)