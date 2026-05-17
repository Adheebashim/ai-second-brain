from fastapi import FastAPI, Form, BackgroundTasks, Response, UploadFile, File, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from memory import save_memory, retrieve_memories
from ai import generate_response, extract_reminder
from reminders import schedule_reminder

app = FastAPI(title="AI Personal Assistant API")

# Mount frontend directory for static UI
import os
os.makedirs("../frontend", exist_ok=True)
app.mount("/ui", StaticFiles(directory="../frontend", html=True), name="frontend")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    user_message = req.message
    
    # 1. Retrieve relevant past context from memory
    memories = retrieve_memories(user_message)
    
    # 2. Generate response using AI and context
    ai_response = generate_response(user_message, memories)
    
    # 3. Save the new user message to memory so the AI remembers it
    save_memory(user_message)
    
    # 4. Return response
    return ChatResponse(response=ai_response)

@app.get("/")
async def root():
    return {"status": "Backend is running", "ui_url": "/ui"}

import pandas as pd
import io

@app.post("/upload-excel")
async def upload_excel(file: UploadFile = File(...)):
    if not file.filename.endswith(('.xlsx', '.csv')):
        return {"error": "Invalid file format. Please upload .xlsx or .csv files."}
        
    try:
        contents = await file.read()
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
            
        # Convert each row to a string memory and save it
        records_saved = 0
        for index, row in df.iterrows():
            row_dict = row.dropna().to_dict()
            if not row_dict:
                continue
            memory_text = f"Data from {file.filename} (Row {index+1}): " + ", ".join([f"{k}: {v}" for k, v in row_dict.items()])
            save_memory(memory_text)
            records_saved += 1
            
        return {"message": f"Successfully processed {file.filename} and memorized {records_saved} rows."}
    except Exception as e:
        return {"error": f"Failed to process file: {str(e)}"}

@app.post("/telegram")
async def telegram_endpoint(request: Request, background_tasks: BackgroundTasks):
    update = await request.json()
    
    if "message" not in update or "text" not in update["message"]:
        return {"status": "ok"}
        
    user_message = update["message"]["text"]
    chat_id = update["message"]["chat"]["id"]
    
    # 1. Check if it's a reminder
    reminder_info = extract_reminder(user_message)
    if reminder_info:
        delay = reminder_info['delay_seconds']
        text = reminder_info['reminder_text']
        # Schedule it in the background
        background_tasks.add_task(schedule_reminder, delay, text, str(chat_id))
        
        # Respond immediately to acknowledge the reminder
        return {
            "method": "sendMessage",
            "chat_id": chat_id,
            "text": f"Got it! I will remind you to '{text}' in {delay} seconds."
        }

    # 2. Retrieve relevant past context from memory
    memories = retrieve_memories(user_message)
    
    # 3. Generate response using AI and context
    ai_response = generate_response(user_message, memories)
    
    # 4. Save the new user message to memory so the AI remembers it
    save_memory(user_message)
    
    # 5. Return Telegram JSON response
    return {
        "method": "sendMessage",
        "chat_id": chat_id,
        "text": ai_response
    }
