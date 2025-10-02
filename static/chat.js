const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const chatInput = document.getElementById('chatInput');
const logoutBtn = document.getElementById('logoutBtn');

const STORAGE_KEY = 'agent_chat_history';

function loadChatHistory() {
    try {
        const history = sessionStorage.getItem(STORAGE_KEY);
        if (history) {
            const messages = JSON.parse(history);
            messages.forEach(msg => {
                addMessage(msg.content, msg.type, false);
            });
        }
    } catch (error) {
        console.error('Error loading chat history:', error);
    }
}

function saveChatHistory(content, type) {
    try {
        const history = sessionStorage.getItem(STORAGE_KEY);
        const messages = history ? JSON.parse(history) : [];
        messages.push({ content, type, timestamp: new Date().toISOString() });
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    } catch (error) {
        console.error('Error saving chat history:', error);
    }
}

function formatMessage(text) {
    let formatted = text
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
    return formatted;
}

function addMessage(content, type, save = true) {
    const welcomeMessage = chatMessages.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const label = document.createElement('div');
    label.className = 'message-label';
    label.textContent = type === 'user' ? 'You' : 'Assistant';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (type === 'assistant') {
        contentDiv.innerHTML = formatMessage(content);
    } else {
        contentDiv.textContent = content;
    }
    
    messageDiv.appendChild(label);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    scrollToBottom();
    
    if (save) {
        saveChatHistory(content, type);
    }
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const message = chatInput.value.trim();
    if (!message) return;
    
    addMessage(message, 'user');
    chatInput.value = '';
    
    const sendButton = chatForm.querySelector('.btn-send');
    sendButton.disabled = true;
    sendButton.textContent = 'Thinking...';
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        
        if (data.success) {
            addMessage(data.message, 'assistant');
        } else {
            addMessage(data.message || 'Sorry, I encountered an error processing your request.', 'assistant');
        }
    } catch (error) {
        addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
    } finally {
        sendButton.disabled = false;
        sendButton.textContent = 'Send';
        chatInput.focus();
    }
});

logoutBtn.addEventListener('click', async () => {
    try {
        const response = await fetch('/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            sessionStorage.removeItem(STORAGE_KEY);
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Logout error:', error);
        window.location.href = '/login';
    }
});

loadChatHistory();
chatInput.focus();
