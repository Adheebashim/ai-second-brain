# Your Final Checklist: What You Need To Do

The code is 100% written and functioning. To fully launch your AI Second Brain, record your demo, and showcase it to the world, please follow these final manual steps.

## 1. 🔑 Get Your API Keys
To make the AI run and connect to Telegram, you need to populate the `backend/.env` file.
- **Groq API Key (Already Done):** You've already got your Llama 3 API key set up.
- **Telegram Bot Token:**
  - Open Telegram and search for **@BotFather**.
  - Send the command `/newbot` and follow the prompts to create your bot.
  - BotFather will give you an HTTP API Token (e.g., `123456789:ABCDEF...`).
  - Paste this token into `backend/.env` as `TELEGRAM_BOT_TOKEN`.

## 2. 📱 Set Up Telegram Webhook
You need to connect Telegram to your local server so it can receive messages.
- **Run Ngrok:**
  - Download and install [Ngrok](https://ngrok.com/).
  - Run this command in your terminal to expose your local server to the internet:
    ```bash
    ngrok http 8000
    ```
  - Copy the `https://...ngrok-free.app` URL it gives you.
- **Set the Webhook:**
  - Open a browser or terminal and run this URL (replace the placeholders with your actual Bot Token and Ngrok URL):
    ```
    https://api.telegram.org/bot<YOUR_TELEGRAM_BOT_TOKEN>/setWebhook?url=https://<YOUR_NGROK_URL>/telegram
    ```
  - You should see a response like `{"ok":true,"result":true,"description":"Webhook was set"}`.

## 3. 🧪 Test Everything End-to-End
Before recording a demo, make sure everything works perfectly.
1. Make sure your FastAPI backend is running (`cd backend` and `python -m uvicorn main:app`).
2. **Test Web UI:** Go to `http://127.0.0.1:8000/ui`, chat with the bot, and drag & drop a sample `.xlsx` or `.csv` file.
3. **Test Telegram:** Open Telegram, find your bot, and send a message. Ask it to remember something, then ask it a question about it.
4. **Test Reminders:** Send a Telegram message saying: *"Remind me to check the oven in 60 seconds."*

## 4. 🎥 Record Your Demo Video
This is crucial for your portfolio, LinkedIn, and GitHub!
- Use a screen recorder (like OBS, Loom, or Windows Snipping Tool).
- **Showcase 1 (The UI):** Show the beautiful dark mode UI. Upload an Excel file and ask the AI a question about the data in the file.
- **Showcase 2 (Telegram):** Put your Telegram chat side-by-side with your terminal. Show yourself texting the AI, the AI answering fast, and setting a background reminder.
- Upload this video to YouTube (Unlisted) or directly to LinkedIn.

## 5. 🚀 Push to GitHub & Update Portfolio
- **Update README:** Open `README.md` and replace the `[Insert Demo Video Link Here]` placeholder with the actual link to your recorded video.
- **Push Code:**
  ```bash
  git add .
  git commit -m "Switched to Telegram Bot Integration and finalized sprint"
  git branch -M main
  git remote add origin https://github.com/yourusername/your-repo-name.git
  git push -u origin main
  ```
- **Post on LinkedIn:** Write a post detailing how you built an Agentic AI Assistant in 3 days using FastAPI, Groq, ChromaDB, and Telegram. Link your GitHub repo and attach the video!
