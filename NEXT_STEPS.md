# Your Final Checklist: Setting Up Your Private Telegram Second Brain

The code is fully optimized for a secure, Telegram-exclusive experience. To deploy your private assistant to the cloud and start using it 24/7, please follow these simple steps.

---

## 1. 🔑 Get Your API Keys & Chat ID

To configure your cloud server, you need credentials from these services:

- **Groq API Key (Already Set up):** Your Llama 3 API key is configured.
- **Telegram Bot Token:**
  - Open Telegram and search for the official account **@BotFather**.
  - Send the command `/newbot` and follow the quick prompts to name your bot.
  - @BotFather will reply with an HTTP API Token (e.g., `123456789:ABCDEF...`). Keep this safe!
- **Pinecone API Key:**
  - Go to [Pinecone.io](https://www.pinecone.io/) and sign up for a free account.
  - Head to the **API Keys** tab and copy your generated key.
- **Your Personal Telegram Chat ID:**
  - Start your FastAPI server locally or on Render (see Step 2 below).
  - Open Telegram and send any text message to your new bot.
  - Because you haven't locked access down yet, your bot will automatically read your message and reply with your **exact Telegram Chat ID** and instructions!
  - Copy this number down to secure your bot.

*Save these four values in your `backend/.env` file for local testing, or enter them directly into your Render settings.*

---

## 2. 🚀 Deploy to Render (Free 24/7 Cloud Hosting)

You need to host the backend in the cloud so it remains online and responsive even when your laptop is turned off.

1. **Push your code to GitHub**:
   Run the following commands in your terminal:
   ```bash
   git add .
   git commit -m "Configure secure Telegram-exclusive chatbot"
   git branch -M main
   git push -u origin main
   ```
2. **Set up Render**:
   - Create a free account on [Render.com](https://render.com/).
   - Click **New > Web Service**.
   - Connect your GitHub account and select this repository.
   - Render automatically reads the `render.yaml` and `Dockerfile` in the root directory.
   - When prompted, add these **Environment Variables**:
     * `GROQ_API_KEY`
     * `TELEGRAM_BOT_TOKEN`
     * `PINECONE_API_KEY`
     * `ALLOWED_TELEGRAM_CHAT_ID` *(Use the number you got in Step 1. Leave blank on first run if you need the bot to tell you your ID).*
   - Click **Create Web Service**. Wait a few minutes for Render to compile and launch the server. It will supply a public URL (e.g., `https://my-second-brain.onrender.com`).

---

## 3. 📱 Set Up the Telegram Webhook

To direct incoming messages from Telegram to your Render server:

- Open a web browser and open this URL (replace the bracketed placeholders with your actual credentials):
  ```text
  https://api.telegram.org/bot<YOUR_TELEGRAM_BOT_TOKEN>/setWebhook?url=https://<YOUR_RENDER_URL>/telegram
  ```
- If successful, you will see the response:
  ```json
  {"ok":true,"result":true,"description":"Webhook was set"}
  ```

---

## 4. 🧪 How to Use Your Private AI Assistant

Once fully deployed and locked down using your `ALLOWED_TELEGRAM_CHAT_ID`, open Telegram and try these private commands:

### 💬 Chat & Query
Send any standard question or note. The bot will search your vector memory in Pinecone, grab relevant historical context, and generate a customized answer. It also records what you say so it learns as you chat!

### ⏰ Add Reminders
Tell the bot to remind you to do something, e.g.:
> *"Remind me to call the landlord in 60 seconds"*

The assistant will extract the task and the delay automatically, scheduling an asynchronous background reminder that will text you when the timer goes off.

### 📊 Direct Spreadsheet Uploads
Drag and drop or attach an Excel (`.xlsx`) or CSV (`.csv`) spreadsheet directly into your Telegram chat.
- The assistant will download it in the background, parse the columns, and upload every row as an individual memory to Pinecone!
- It will confirm in-chat: `"✅ Successfully processed and memorized X rows from your file!"`
- You can immediately ask queries about that data (e.g. *"Who are the highest performing sales reps in the spreadsheet I just sent?"*).
