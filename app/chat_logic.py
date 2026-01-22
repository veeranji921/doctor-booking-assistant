from openai import OpenAI
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

from typing import List, Dict
import streamlit as st
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from config import Config
from booking_flow import BookingFlowManager
from tools import ToolRouter

class ChatLogic:
    """Handles chat logic, intent detection, and conversation flow"""
    
    def __init__(self, rag_pipeline, database):
        # Initialize client based on config
        if Config.USE_GROQ and GROQ_AVAILABLE:
            self.client = Groq(api_key=Config.GROQ_API_KEY)
            self.model = Config.GROQ_MODEL
            self.use_groq = True
        else:
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
            self.model = Config.OPENAI_MODEL
            self.use_groq = False
        
        self.booking_flow = BookingFlowManager()
        self.tool_router = ToolRouter(rag_pipeline, database)
        self.conversation_history = []
    
    def add_to_history(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({"role": role, "content": content})
        
        # Keep only last MAX_MEMORY_MESSAGES
        if len(self.conversation_history) > Config.MAX_MEMORY_MESSAGES:
            self.conversation_history = self.conversation_history[-Config.MAX_MEMORY_MESSAGES:]
    
    def detect_intent(self, message: str) -> str:
        """Detect user intent: booking, question, or general"""
        booking_keywords = ['book', 'appointment', 'schedule', 'reserve', 'consultation', 
                           'visit', 'checkup', 'examination']
        
        message_lower = message.lower()
        
        # Check for booking intent
        if any(keyword in message_lower for keyword in booking_keywords):
            return "booking"
        
        # Check for question intent
        if any(word in message_lower for word in ['what', 'when', 'where', 'how', 'who', 'why', '?']):
            return "question"
        
        return "general"
    
    def get_rag_response(self, query: str) -> str:
        """Get response using RAG"""
        # Retrieve context
        context = self.tool_router.route_rag_query(query)
        
        if "No documents" in context or "couldn't find" in context:
            return context
        
        # Create prompt with context
        messages = [
            {"role": "system", "content": Config.SYSTEM_PROMPT},
            {"role": "user", "content": f"Context from documents:\n{context}\n\nQuestion: {query}\n\nPlease answer based on the context provided."}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def handle_booking_flow(self, message: str) -> str:
        """Handle booking conversation flow"""
        # Check if awaiting confirmation
        if self.booking_flow.awaiting_confirmation:
            confirmation = self.booking_flow.is_confirmation_response(message)
            
            if confirmation is True:
                # Process booking
                return self.process_booking()
            elif confirmation is False:
                # Reset booking
                self.booking_flow.reset()
                return "Booking cancelled. Feel free to start a new booking anytime!"
            else:
                return "I didn't understand. Please reply with 'yes' to confirm or 'no' to cancel."
        
        # Extract details from message
        extracted = self.booking_flow.extract_details_from_message(message)
        self.booking_flow.update_details(extracted)
        
        # Check if all details are collected
        if self.booking_flow.booking_details.is_complete():
            # Validate details
            is_valid, error_msg = self.booking_flow.validate_details()
            
            if not is_valid:
                return error_msg
            
            # Ask for confirmation
            self.booking_flow.awaiting_confirmation = True
            return self.booking_flow.get_confirmation_message()
        
        # Ask next question
        next_question = self.booking_flow.get_next_question()
        
        if extracted:
            # Acknowledge received information
            acknowledgment = "Thank you! "
            return acknowledgment + next_question
        
        return next_question
    
    def process_booking(self) -> str:
        """Process and save the booking"""
        booking_data = self.booking_flow.booking_details.to_dict()
        
        # Save to database
        db_result = self.tool_router.route_booking_save(booking_data)
        
        if not db_result['success']:
            return f"Sorry, there was an error saving your booking: {db_result['message']}"
        
        booking_id = db_result['booking_id']
        
        # Send confirmation email
        email_result = self.tool_router.route_email_send(booking_data, booking_id)
        
        # Reset booking flow
        self.booking_flow.reset()
        
        # Prepare response
        response = f"✅ **Booking Confirmed!**\n\n"
        response += f"Your booking ID is: **#{booking_id}**\n\n"
        response += f"📧 "
        
        if email_result['success']:
            response += "A confirmation email has been sent to your email address."
        else:
            response += f"Note: Email could not be sent ({email_result['message']}), but your booking was saved successfully."
        
        return response
    
    def generate_response(self, message: str) -> str:
        """Generate response based on message and intent"""
        # Add user message to history
        self.add_to_history("user", message)
        
        # Detect intent
        intent = self.detect_intent(message)
        
        # Handle based on intent
        if intent == "booking" or self.booking_flow.awaiting_confirmation or \
           not self.booking_flow.booking_details.is_complete() and \
           self.booking_flow.booking_details.to_dict() != {'name': None, 'email': None, 
                                                            'phone': None, 'booking_type': None, 
                                                            'date': None, 'time': None}:
            response = self.handle_booking_flow(message)
        elif intent == "question":
            response = self.get_rag_response(message)
        else:
            # General conversation
            messages = [
                {"role": "system", "content": Config.SYSTEM_PROMPT}
            ] + self.conversation_history[-10:] + [
                {"role": "user", "content": message}
            ]
            
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=300
                )
                response = completion.choices[0].message.content
            except Exception as e:
                response = f"I apologize, but I encountered an error: {str(e)}"
        
        # Add assistant response to history
        self.add_to_history("assistant", response)
        
        return response
    
    def reset_conversation(self):
        """Reset conversation history and booking flow"""
        self.conversation_history = []
        self.booking_flow.reset()