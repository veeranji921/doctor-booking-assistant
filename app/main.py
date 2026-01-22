import streamlit as st
import sys
import os

# Add directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, current_dir)

# Import from same directory using direct imports
from config import Config
from rag_pipeline import RAGPipeline
from chat_logic import ChatLogic
from admin_dashboard import AdminDashboard

# Import database
sys.path.insert(0, os.path.join(parent_dir, 'db'))
from database import Database

# Page configuration
st.set_page_config(
    page_title="AI Booking Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        color: #155724;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.5rem;
        color: #721c24;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if 'database' not in st.session_state:
        st.session_state.database = Database(Config.DB_PATH)
    
    if 'rag_pipeline' not in st.session_state:
        st.session_state.rag_pipeline = RAGPipeline()
    
    if 'chat_logic' not in st.session_state:
        st.session_state.chat_logic = ChatLogic(
            st.session_state.rag_pipeline,
            st.session_state.database
        )
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'pdfs_uploaded' not in st.session_state:
        st.session_state.pdfs_uploaded = False

# Sidebar
def render_sidebar():
    """Render sidebar with navigation and PDF upload"""
    with st.sidebar:
        st.title("🏥 Medical Booking Assistant")
        st.markdown("---")
        
        # Navigation
        page = st.radio(
            "Navigation",
            ["💬 Chat", "📊 Admin Dashboard"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # PDF Upload Section
        st.subheader("📄 Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload clinic information PDFs",
            type=['pdf'],
            accept_multiple_files=True,
            help="Upload PDFs containing clinic information, services, policies, etc."
        )
        
        if uploaded_files and st.button("Process PDFs"):
            with st.spinner("Processing PDFs..."):
                try:
                    success = st.session_state.rag_pipeline.process_pdfs(uploaded_files)
                    if success:
                        st.session_state.pdfs_uploaded = True
                        st.success(f"✅ Successfully processed {len(uploaded_files)} PDF(s)")
                    else:
                        st.error("❌ Error processing PDFs")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        # Status indicators
        st.markdown("---")
        st.subheader("System Status")
        
        if st.session_state.pdfs_uploaded:
            st.success("✅ RAG System: Active")
        else:
            st.warning("⚠️ RAG System: No documents uploaded")
        
        # Reset conversation
        st.markdown("---")
        if st.button("🔄 Reset Conversation"):
            st.session_state.messages = []
            st.session_state.chat_logic.reset_conversation()
            st.success("Conversation reset!")
            st.rerun()
        
        # Info
        st.markdown("---")
        st.info("💡 **Tip:** Upload clinic PDFs to answer questions about services, hours, and policies.")
        
        return page

# Chat page
def render_chat_page():
    """Render the chat interface"""
    st.title("💬 AI Booking Assistant")
    st.markdown("Ask questions or book an appointment!")
    st.markdown("---")
    
    # Welcome message
    if len(st.session_state.messages) == 0:
        welcome_message = """
        👋 Welcome to the Medical Booking Assistant!
        
        I can help you with:
        - 📅 Booking appointments
        - 📄 Answering questions about our clinic (upload PDFs first)
        - ℹ️ General information
        
        How can I assist you today?
        """
        st.session_state.messages.append({
            "role": "assistant",
            "content": welcome_message
        })
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.chat_logic.generate_response(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

# Admin dashboard page
def render_admin_page():
    """Render the admin dashboard"""
    admin_dashboard = AdminDashboard(st.session_state.database)
    admin_dashboard.render()

# Main application
def main():
    """Main application entry point"""
    init_session_state()
    
    # Render sidebar and get selected page
    page = render_sidebar()
    
    # Render selected page
    if page == "💬 Chat":
        render_chat_page()
    else:
        render_admin_page()

if __name__ == "__main__":
    main()