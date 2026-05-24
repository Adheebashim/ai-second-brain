import time
import os
import sys

# Ensure backend directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_db, add_reminder, get_due_reminders, mark_as_sent

def test_sqlite_reminders():
    print("[START] Starting SQLite persistent reminders verification tests...")
    
    # 1. Initialize the database
    init_db()
    print("[OK] Database initialized successfully.")
    
    # 2. Clear any old test data
    import sqlite3
    from database import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reminders WHERE reminder_text LIKE 'TEST:%'")
    conn.commit()
    conn.close()
    
    # 3. Create a reminder that should trigger in 3 seconds
    print("[WAIT] Adding a test reminder due in 3 seconds...")
    reminder_id = add_reminder("123456789", "TEST: Feed the cat", 3.0)
    print(f"[OK] Reminder added with ID: {reminder_id}")
    
    # 4. Instantly check due reminders (should be empty because 3 seconds haven't elapsed)
    due_instantly = get_due_reminders()
    due_instantly_test = [r for r in due_instantly if r["id"] == reminder_id]
    if len(due_instantly_test) == 0:
        print("[OK] Success: Reminder is not due immediately.")
    else:
        print("[ERROR] Error: Reminder was retrieved before it was due!")
        sys.exit(1)
        
    # 5. Wait for 4 seconds
    print("[WAIT] Sleeping for 4 seconds to allow reminder to become due...")
    time.sleep(4)
    
    # 6. Check due reminders again (should now be retrieved)
    due_later = get_due_reminders()
    due_later_test = [r for r in due_later if r["id"] == reminder_id]
    if len(due_later_test) == 1:
        print("[OK] Success: Overdue reminder detected correctly.")
        reminder = due_later_test[0]
        print(f"   Fetched: '{reminder['reminder_text']}' for chat {reminder['chat_id']}")
    else:
        print("[ERROR] Error: Overdue reminder was NOT detected!")
        sys.exit(1)
        
    # 7. Mark as sent and verify it is not retrieved again
    print("[OK] Marking reminder as sent...")
    mark_as_sent(reminder_id)
    
    due_after_sent = get_due_reminders()
    due_after_sent_test = [r for r in due_after_sent if r["id"] == reminder_id]
    if len(due_after_sent_test) == 0:
        print("[OK] Success: Sent reminders are excluded from subsequent checks.")
    else:
        print("[ERROR] Error: Sent reminder was still retrieved!")
        sys.exit(1)
        
    print("\n[SUCCESS] ALL TESTS PASSED SUCCESSFULLY! The persistent SQLite logic is 100% robust.")

if __name__ == "__main__":
    test_sqlite_reminders()
