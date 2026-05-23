FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the application code
COPY . .

# Change to the backend directory where main.py is located
WORKDIR /app/backend

# Run the FastAPI server on port 8000, or the port specified by Render
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
