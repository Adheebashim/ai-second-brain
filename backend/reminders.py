import os
import asyncio
import requests
from dotenv import load_dotenv
from database import add_reminder, get_due_reminders, mark_as_sent

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

def add_reminder_to_db(chat_id: str, text: str, delay_seconds: float) -> str:
    """
    Inserts a reminder into the database with a calculated due timestamp.
    """
    print(f"Persisting reminder to database: '{text}' in {delay_seconds} seconds for chat {chat_id}")
    return add_reminder(chat_id, text, delay_seconds)

async def check_due_reminders():
    """
    Fetches due reminders from the database, sends them, and marks them as sent.
    """
    due_reminders = get_due_reminders()
    if not due_reminders:
        return

    print(f"Found {len(due_reminders)} due reminders. Processing...")
    for reminder in due_reminders:
        try:
            # Send the telegram alert
            send_telegram_message(
                reminder["chat_id"], 
                f"⏰ Reminder: {reminder['reminder_text']}"
            )
            # Mark it as sent in SQLite to avoid duplication
            mark_as_sent(reminder["id"])
        except Exception as e:
            print(f"Error processing reminder {reminder['id']}: {e}")

async def run_scheduler_loop():
    """
    Persistent active background task that polls SQLite for due reminders every 10 seconds.
    """
    print("Persistent background reminder loop started.")
    while True:
        try:
            await check_due_reminders()
        except Exception as e:
            print(f"Exception inside reminder scheduler loop: {e}")
        await asyncio.sleep(10)

def start_reminder_scheduler():
    """
    Schedules the background polling task in the running asyncio event loop.
    """
    asyncio.create_task(run_scheduler_loop())
