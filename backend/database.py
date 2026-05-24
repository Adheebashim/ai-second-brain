import sqlite3
import os
import uuid
import time

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reminders.db")

def init_db():
    """
    Initializes the SQLite database and creates the reminders table if it doesn't exist.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id TEXT PRIMARY KEY,
            chat_id TEXT NOT NULL,
            reminder_text TEXT NOT NULL,
            due_timestamp REAL NOT NULL,
            sent INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def add_reminder(chat_id: str, reminder_text: str, delay_seconds: float) -> str:
    """
    Calculates the target timestamp and saves the reminder to the SQLite database.
    """
    reminder_id = str(uuid.uuid4())
    due_timestamp = time.time() + delay_seconds
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO reminders (id, chat_id, reminder_text, due_timestamp, sent) VALUES (?, ?, ?, ?, ?)",
        (reminder_id, chat_id, reminder_text, due_timestamp, 0)
    )
    conn.commit()
    conn.close()
    return reminder_id

def get_due_reminders() -> list[dict]:
    """
    Fetches all unsent reminders that have a due_timestamp less than or equal to the current time.
    """
    current_time = time.time()
    conn = sqlite3.connect(DB_PATH)
    # Return rows as dictionaries for ease of use
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, chat_id, reminder_text, due_timestamp FROM reminders WHERE sent = 0 AND due_timestamp <= ?",
        (current_time,)
    )
    rows = cursor.fetchall()
    
    due_list = []
    for row in rows:
        due_list.append({
            "id": row["id"],
            "chat_id": row["chat_id"],
            "reminder_text": row["reminder_text"],
            "due_timestamp": row["due_timestamp"]
        })
        
    conn.close()
    return due_list

def mark_as_sent(reminder_id: str):
    """
    Marks a reminder as sent in the database to prevent duplicate notifications.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE reminders SET sent = 1 WHERE id = ?",
        (reminder_id,)
    )
    conn.commit()
    conn.close()
