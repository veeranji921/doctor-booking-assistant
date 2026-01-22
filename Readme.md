# 🏥 AI Booking Assistant

A comprehensive AI-powered booking assistant for medical appointments with RAG capabilities, built with Streamlit and OpenAI.

## 📋 Features

- **💬 Conversational Chat Interface**: Natural language interaction for booking appointments
- **📄 RAG (Retrieval-Augmented Generation)**: Upload PDFs and get intelligent answers
- **🗓️ Smart Booking System**: Multi-turn conversation for collecting booking details
- **✅ Confirmation Flow**: Explicit user confirmation before saving bookings
- **📧 Email Notifications**: Automatic confirmation emails after booking
- **📊 Admin Dashboard**: View, search, and export all bookings
- **💾 Data Persistence**: SQLite database for storing bookings and customers
- **🧠 Conversational Memory**: Maintains context for last 20-25 messages

## 🏗️ Architecture

```
doctor-booking-assistant/
├── app/
│   ├── main.py              # Streamlit application entry point
│   ├── chat_logic.py         # Intent detection & conversation management
│   ├── booking_flow.py       # Booking slot filling & validation
│   ├── rag_pipeline.py       # PDF processing & vector store
│   ├── tools.py              # RAG, Database, and Email tools
│   ├── admin_dashboard.py    # Admin interface
│   └── config.py             # Configuration settings
├── db/
│   ├── database.py           # SQLite database operations
│   └── models.py             # Data models
├── docs/
│   └── sample_clinic_info.pdf
├── .streamlit/
│   └── secrets.toml          # API keys and secrets
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- Gmail account (for email confirmations)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd doctor-booking-assistant
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure secrets**

Create `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "sk-your-openai-api-key"
EMAIL_ADDRESS = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"
```

**Gmail App Password Setup:**
- Go to Google Account settings
- Enable 2-Factor Authentication
- Generate an App Password for "Mail"
- Use this password in secrets.toml

4. **Run the application**
```bash
streamlit run app/main.py
```

## 📖 Usage Guide

### For Users

1. **Upload Documents** (Optional)
   - Use the sidebar to upload clinic information PDFs
   - Click "Process PDFs" to enable RAG capabilities

2. **Book an Appointment**
   - Start a conversation: "I want to book an appointment"
   - Provide details when asked:
     - Name
     - Email
     - Phone number
     - Appointment type
     - Date (YYYY-MM-DD format)
     - Time (HH:MM format)
   - Confirm your booking
   - Receive booking ID and email confirmation

3. **Ask Questions**
   - Ask about clinic services, policies, hours, etc.
   - Get answers based on uploaded documents

### For Admins

1. Navigate to "📊 Admin Dashboard"
2. View all bookings with statistics
3. Search by name, email, or date
4. Export bookings to CSV

## 🛠️ Technical Details

### RAG Pipeline
- **Text Extraction**: PyPDF for PDF processing
- **Chunking**: RecursiveCharacterTextSplitter (1000 chars, 200 overlap)
- **Embeddings**: OpenAI text-embedding-ada-002
- **Vector Store**: ChromaDB (in-memory)
- **Retrieval**: Top-3 similar chunks

### Booking Flow
1. Intent detection (booking vs question vs general)
2. Extract known details from user message
3. Ask for missing information
4. Validate all fields (email, date, time format)
5. Present summary for confirmation
6. Save to database on confirmation
7. Send email confirmation

### Database Schema

**customers**
- customer_id (PRIMARY KEY)
- name
- email
- phone
- created_at

**bookings**
- id (PRIMARY KEY)
- customer_id (FOREIGN KEY)
- booking_type
- date
- time
- status
- created_at

### Tools Implementation

1. **RAG Tool**: Retrieves context from vector store
2. **Booking Persistence Tool**: Saves bookings to SQLite
3. **Email Tool**: Sends HTML confirmation emails via SMTP

## 🔧 Configuration

Edit `app/config.py` to customize:
- OpenAI model selection
- Memory settings (max messages)
- Booking types available
- RAG parameters (chunk size, top-k)
- System prompt

## 📊 Deployment

### Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy from your repository
4. Add secrets in Streamlit Cloud dashboard:
   - OPENAI_API_KEY
   - EMAIL_ADDRESS
   - EMAIL_PASSWORD

### Environment Variables

If not using Streamlit secrets, set:
```bash
export OPENAI_API_KEY="your-key"
export EMAIL_ADDRESS="your-email"
export EMAIL_PASSWORD="your-password"
```

## ✅ Error Handling

The system handles:
- ❌ Invalid email formats
- ❌ Past dates
- ❌ Invalid time formats
- ❌ Missing PDF uploads
- ❌ Database connection errors
- ❌ Email delivery failures
- ❌ OpenAI API errors

User-friendly messages are displayed for all errors.

## 🎯 Booking Types Supported

- General Consultation
- Dental Checkup
- Eye Examination
- Blood Test
- Vaccination
- Follow-up Visit
- Emergency Consultation

(Customizable in `config.py`)

## 🔐 Security Notes

- API keys stored in `.streamlit/secrets.toml` (gitignored)
- Use Gmail App Passwords, not regular passwords
- SQLite database file excluded from git
- No sensitive data logged

## 🐛 Troubleshooting

**PDFs not processing?**
- Check file format is PDF
- Ensure OpenAI API key is valid
- Check console for errors

**Email not sending?**
- Verify Gmail App Password is correct
- Enable 2-Factor Authentication on Gmail
- Check SMTP settings in config.py

**Database issues?**
- Delete `bookings.db` and restart
- Check file permissions
- Verify SQLite is installed

## 📈 Future Enhancements

- [ ] Speech-to-Text (STT) integration
- [ ] Text-to-Speech (TTS) responses
- [ ] Booking cancellation/rescheduling
- [ ] SMS notifications
- [ ] Calendar integration
- [ ] Multi-language support
- [ ] Payment processing

## 📝 License

This project is for educational purposes as part of an AI Engineer assignment.

## 👥 Contact

For issues or questions, please contact the development team.

---

**Built with ❤️ using Streamlit, OpenAI, and Python**