const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const uploadStatus = document.getElementById('upload-status');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const chatMessages = document.getElementById('chat-messages');

// === Drag and Drop Logic ===
dropZone.addEventListener('click', () => fileInput.click());

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
});

dropZone.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    if (files.length) handleFiles(files[0]);
});

fileInput.addEventListener('change', function() {
    if (this.files.length) handleFiles(this.files[0]);
});

function handleFiles(file) {
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.csv')) {
        showStatus('Only .xlsx or .csv files are allowed.', 'error');
        return;
    }
    
    uploadFile(file);
}

async function uploadFile(file) {
    showStatus('Uploading and analyzing...', '');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/upload-excel', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        if (response.ok) {
            showStatus(data.message || 'File analyzed successfully!', 'success');
        } else {
            showStatus(data.error || 'Upload failed.', 'error');
        }
    } catch (error) {
        showStatus('Network error occurred.', 'error');
    }
}

function showStatus(msg, type) {
    uploadStatus.textContent = msg;
    uploadStatus.className = 'status-msg ' + type;
}

// === Chat Logic ===

sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Add user message to UI
    appendMessage(message, 'user');
    chatInput.value = '';
    
    // Show typing indicator
    const typingId = showTypingIndicator();
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        removeTypingIndicator(typingId);
        
        if (response.ok) {
            appendMessage(data.response, 'ai');
        } else {
            appendMessage('Sorry, I encountered an error.', 'ai');
        }
    } catch (error) {
        removeTypingIndicator(typingId);
        appendMessage('Network error. Is the server running?', 'ai');
    }
}

function appendMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}-message`;
    
    const icon = sender === 'ai' ? '<i class="fa-solid fa-robot"></i>' : '<i class="fa-solid fa-user"></i>';
    
    // Convert newlines to <br> for AI responses
    const formattedText = text.replace(/\n/g, '<br>');
    
    msgDiv.innerHTML = `
        <div class="avatar">${icon}</div>
        <div class="content">${formattedText}</div>
    `;
    
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const id = 'typing-' + Date.now();
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message ai-message';
    msgDiv.id = id;
    
    msgDiv.innerHTML = `
        <div class="avatar"><i class="fa-solid fa-robot"></i></div>
        <div class="content">
            <div class="typing-indicator">
                <div class="dot"></div><div class="dot"></div><div class="dot"></div>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}
