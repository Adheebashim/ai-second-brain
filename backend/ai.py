import os
import json
from groq import Groq
from dotenv import load_dotenv

# Load environment variables (e.g., GROQ_API_KEY)
load_dotenv()

# Initialize Groq client
# The client automatically picks up the GROQ_API_KEY from the environment
try:
    client = Groq()
except Exception as e:
    client = None
    print(f"Warning: Could not initialize Groq client. Check your GROQ_API_KEY. Error: {e}")

def generate_response(user_message: str, retrieved_memories: list[str]) -> str:
    """
    Generates a response using Groq, incorporating past memories as context.
    """
    if not client:
        return "Error: Groq client is not initialized. Please ensure your GROQ_API_KEY is set in the .env file."
        
    # Build the system prompt with context
    system_prompt = (
        "You are a highly capable personal AI assistant. "
        "You are concise, professional, and helpful. "
        "Below are relevant memories or notes the user has shared with you in the past. "
        "Use them to answer the user's current message if applicable.\n\n"
        "--- Past Memories ---\n"
    )
    
    if retrieved_memories:
        for i, memory in enumerate(retrieved_memories, 1):
            system_prompt += f"{i}. {memory}\n"
    else:
        system_prompt += "No relevant past memories found.\n"
        
    system_prompt += "\n---------------------\n"
    system_prompt += "Answer the user's message appropriately."
    
    try:
        # Call Groq API
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            model="llama-3.1-8b-instant", # Fast and capable model
            temperature=0.5,
            max_tokens=1024,
        )
        
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        return f"An error occurred while communicating with the AI: {str(e)}"

def extract_reminder(user_message: str) -> dict | None:
    """
    Checks if a message contains a reminder request.
    Returns a dictionary with 'delay_seconds' and 'reminder_text' if it is a reminder.
    Returns None otherwise.
    """
    if not client:
        return None

    prompt = (
        "You are an AI assistant. Analyze the following user message to determine if they are asking to set a reminder.\n"
        "If they are, extract the delay in seconds until the reminder should go off, and the text of the reminder.\n"
        "Respond ONLY with a JSON object in this exact format: {\"is_reminder\": true, \"delay_seconds\": 120, \"reminder_text\": \"check the oven\"}.\n"
        "If it is not a reminder, respond with: {\"is_reminder\": false}.\n"
        f"User message: {user_message}"
    )

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        
        response_json = json.loads(chat_completion.choices[0].message.content)
        if response_json.get("is_reminder"):
            return {
                "delay_seconds": response_json.get("delay_seconds", 0),
                "reminder_text": response_json.get("reminder_text", "")
            }
        return None
    except Exception as e:
        print(f"Error extracting reminder: {e}")
        return None
