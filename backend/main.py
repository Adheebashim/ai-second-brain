from fastapi import FastAPI, BackgroundTasks, Request
from pydantic import BaseModel
from memory import save_memory, retrieve_memories
from ai import generate_response, extract_reminder
from reminders import schedule_reminder
import os
import requests
import io
import pandas as pd
from dotenv import load_dotenv

# Load configurations
load_dotenv()

app = FastAPI(title="AI Second Brain - Telegram Private API")

ALLOWED_TELEGRAM_CHAT_ID = os.environ.get("ALLOWED_TELEGRAM_CHAT_ID", "").strip()
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()

@app.get("/")
async def root():
    """
    Health check endpoint for Render and other cloud platforms.
    """
    return {
        "status": "AI Second Brain is running",
        "secure_telegram_active": bool(ALLOWED_TELEGRAM_CHAT_ID),
        "telegram_endpoint": "/telegram"
    }

@app.post("/telegram")
async def telegram_endpoint(request: Request, background_tasks: BackgroundTasks):
    """
    Unified Telegram Bot Webhook.
    Handles text chat, background reminders, security checking, and direct spreadsheet processing.
    """
    update = await request.json()
    
    if "message" not in update:
        return {"status": "ok"}
        
    message_data = update["message"]
    chat_id = message_data.get("chat", {}).get("id")
    
    if chat_id is None:
        return {"status": "ok"}
        
    # --- 1. Security & Configuration Helper ---
    if not ALLOWED_TELEGRAM_CHAT_ID:
        # Prompt user with their Chat ID if the bot has not been secured yet
        return {
            "method": "sendMessage",
            "chat_id": chat_id,
            "text": (
                f"👋 Hello! Your AI Second Brain is successfully running.\n\n"
                f"🔒 To secure this assistant and lock it exclusively to your account, "
                f"please add this variable to your backend/.env file (or your Render Environment Variables):\n\n"
                f"ALLOWED_TELEGRAM_CHAT_ID=\"{chat_id}\"\n\n"
                f"After updating this variable and restarting the server, I will respond only to you!"
            )
        }
    elif str(chat_id) != ALLOWED_TELEGRAM_CHAT_ID:
        # Silently log and reject unauthorized access
        print(f"Blocked unauthorized access from Telegram chat ID: {chat_id}")
        return {
            "method": "sendMessage",
            "chat_id": chat_id,
            "text": "❌ Access denied. This is a private AI Second Brain."
        }

    # --- 2. File Upload Handling (Excel / CSV) ---
    if "document" in message_data:
        doc = message_data["document"]
        file_name = doc.get("file_name", "")
        file_id = doc.get("file_id")
        
        if not file_name.endswith(('.xlsx', '.csv')):
            return {
                "method": "sendMessage",
                "chat_id": chat_id,
                "text": "⚠️ Unsupported format. Please send an Excel (.xlsx) or CSV (.csv) file."
            }
            
        if not TELEGRAM_BOT_TOKEN:
            return {
                "method": "sendMessage",
                "chat_id": chat_id,
                "text": "❌ Server configuration error: TELEGRAM_BOT_TOKEN is not defined in the environment."
            }
            
        try:
            # Request file path from Telegram API
            get_file_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}"
            file_info_resp = requests.get(get_file_url)
            file_info_resp.raise_for_status()
            file_info = file_info_resp.json()
            
            if not file_info.get("ok"):
                raise Exception("Could not fetch file download path from Telegram API.")
                
            file_path = file_info["result"]["file_path"]
            download_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
            
            # Download file contents
            file_content_resp = requests.get(download_url)
            file_content_resp.raise_for_status()
            contents = file_content_resp.content
            
            # Parse using Pandas
            if file_name.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(contents))
            else:
                df = pd.read_excel(io.BytesIO(contents))
                
            # Process and store each row in vector memory
            records_saved = 0
            for index, row in df.iterrows():
                row_dict = row.dropna().to_dict()
                if not row_dict:
                    continue
                memory_text = f"Data from {file_name} (Row {index+1}): " + ", ".join([f"{k}: {v}" for k, v in row_dict.items()])
                save_memory(memory_text)
                records_saved += 1
                
            return {
                "method": "sendMessage",
                "chat_id": chat_id,
                "text": f"✅ Successfully processed and memorized {records_saved} rows from your file '{file_name}'!"
            }
            
        except Exception as e:
            print(f"Error processing document upload: {e}")
            return {
                "method": "sendMessage",
                "chat_id": chat_id,
                "text": f"❌ Failed to process spreadsheet: {str(e)}"
            }

    # --- 3. Chat / Text Message Handling ---
    if "text" in message_data:
        user_message = message_data["text"]
        
        # 3a. Extract and schedule background reminders
        reminder_info = extract_reminder(user_message)
        if reminder_info:
            delay = reminder_info['delay_seconds']
            text = reminder_info['reminder_text']
            # Schedule asynchronous reminder
            background_tasks.add_task(schedule_reminder, delay, text, str(chat_id))
            
            return {
                "method": "sendMessage",
                "chat_id": chat_id,
                "text": f"⏰ Got it! I will remind you to '{text}' in {delay} seconds."
            }

        # 3b. Regular Chat with Vector Memory Context
        # Retrieve relevant memories
        memories = retrieve_memories(user_message)
        
        # Generate LLM response
        ai_response = generate_response(user_message, memories)
        
        # Store user's message in Pinecone
        save_memory(user_message)
        
        return {
            "method": "sendMessage",
            "chat_id": chat_id,
            "text": ai_response
        }
        
    return {"status": "ok"}
