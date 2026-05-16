import os
import asyncio
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

def send_whatsapp_message(to_number: str, body: str):
    """
    Synchronous function to send a WhatsApp message using Twilio.
    """
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_number = os.environ.get("TWILIO_PHONE_NUMBER")
    
    if not account_sid or not auth_token or not from_number:
        print("Error: Twilio credentials not fully set in .env")
        return
    
    if account_sid == "your_twilio_account_sid":
        print("Warning: Twilio credentials are still placeholders.")
        return

    client = Client(account_sid, auth_token)

    try:
        message = client.messages.create(
            from_=from_number,
            body=body,
            to=to_number
        )
        print(f"Reminder sent successfully. SID: {message.sid}")
    except Exception as e:
        print(f"Failed to send reminder via Twilio: {e}")

async def schedule_reminder(delay_seconds: int, text: str, to_number: str):
    """
    Asynchronous task that waits for delay_seconds and then sends a WhatsApp message.
    """
    print(f"Reminder scheduled for {delay_seconds} seconds from now for {to_number}")
    await asyncio.sleep(delay_seconds)
    send_whatsapp_message(to_number, f"⏰ Reminder: {text}")
