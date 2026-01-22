import os
import streamlit as st

class Config:
    """Configuration settings for the application"""
    
    # LLM Settings - Choose your provider
    USE_GROQ = True  # Set to True to use Groq (free), False for OpenAI
    
    # OpenAI Settings
    OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
    OPENAI_MODEL = "gpt-3.5-turbo"
    
    # Groq Settings (Free alternative)
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
    GROQ_MODEL = "llama-3.3-70b-versatile"  # Updated to current model
    
    # Embedding Settings - Choose between OpenAI or Free alternatives
    USE_FREE_EMBEDDINGS = True  # Set to True to use free embeddings
    EMBEDDING_MODEL = "text-embedding-ada-002"  # Only used if USE_FREE_EMBEDDINGS = False
    
    # Email Settings
    EMAIL_ADDRESS = st.secrets.get("EMAIL_ADDRESS", os.getenv("EMAIL_ADDRESS"))
    EMAIL_PASSWORD = st.secrets.get("EMAIL_PASSWORD", os.getenv("EMAIL_PASSWORD"))
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    
    # Database Settings
    DB_PATH = "bookings.db"
    
    # RAG Settings
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    TOP_K_RESULTS = 3
    
    # Memory Settings
    MAX_MEMORY_MESSAGES = 25
    
    # Booking Types
    BOOKING_TYPES = [
        "General Consultation",
        "Dental Checkup",
        "Eye Examination",
        "Blood Test",
        "Vaccination",
        "Follow-up Visit",
        "Emergency Consultation"
    ]
    
    # System Prompt
    SYSTEM_PROMPT = """You are a helpful AI assistant for a medical clinic booking system. 
    You can:
    1. Answer questions about the clinic using the provided documents
    2. Help users book appointments
    3. Provide general information
    
    When booking:
    - Be friendly and conversational
    - Collect: name, email, phone, booking type, date, and time
    - Confirm all details before finalizing
    - Only book after explicit user confirmation
    
    Be concise and helpful."""