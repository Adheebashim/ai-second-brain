# AI Second Brain

Welcome to my AI Second Brain! This is a comprehensive 3-day build of a personal AI Assistant that integrates deeply into my daily workflow.

## Features

- **🧠 Persistent Vector Memory**: Powered by ChromaDB. It remembers our conversations and past facts.
- **📱 WhatsApp Integration**: Chat with the assistant anywhere via Twilio.
- **⏰ Smart Reminders**: Automatically extracts reminders and schedules them using background tasks.
- **📊 Excel & CSV Analysis**: Upload your data files, and the AI will analyze and memorize the rows.
- **⚡ Ultra-fast AI**: Powered by Groq and Llama 3.1 8B Instant.
- **✨ Premium UI**: Beautiful, glassmorphic dark-mode web interface for chatting and file uploads.

## Tech Stack

- **Backend**: FastAPI, Python, Pandas, BackgroundTasks
- **AI/ML**: Groq API (Llama 3.1), ChromaDB, Sentence-Transformers
- **Frontend**: Vanilla HTML/CSS/JS (Glassmorphism design)
- **Integrations**: Twilio (WhatsApp webhook)

## Getting Started

1. Clone the repo
2. Create a virtual environment and install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Set your environment variables in `.env`:
   ```env
   GROQ_API_KEY=your_key
   TWILIO_ACCOUNT_SID=your_sid
   TWILIO_AUTH_TOKEN=your_token
   TWILIO_PHONE_NUMBER=whatsapp:+14155238886
   ```
4. Run the server:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```
5. Open `http://127.0.0.1:8000/ui` to access the web interface!

## Demo Video

[Insert Demo Video Link Here]
