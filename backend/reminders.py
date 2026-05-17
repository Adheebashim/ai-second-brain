import os
import asyncio
import requests
from dotenv import load_dotenv

load_dotenv()

def send_telegram_message(chat_id: str, text: str):
    """
    Synchronous function to send a Telegram message using the Bot API.
    """
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    
    if not bot_token or bot_token == "your_telegram_bot_token":
        print("Error: TELEGRAM_BOT_TOKEN not set in .env")
        return
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"Reminder sent successfully to chat {chat_id}.")
    except Exception as e:
        print(f"Failed to send reminder via Telegram: {e}")

async def schedule_reminder(delay_seconds: int, text: str, chat_id: str):
    """
    Asynchronous task that waits for delay_seconds and then sends a Telegram message.
    """
    print(f"Reminder scheduled for {delay_seconds} seconds from now for chat {chat_id}")
    await asyncio.sleep(delay_seconds)
    send_telegram_message(chat_id, f"⏰ Reminder: {text}")
