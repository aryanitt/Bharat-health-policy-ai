const messagesContainer = document.getElementById('messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const loading = document.getElementById('loading');
const quickQuestions = document.querySelectorAll('.q-btn');

// Chat History State
let chatHistory = [];

function addMessage(text, sender) {
    const div = document.createElement('div');
    div.className = `message ${sender}`;

    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = sender === 'user' ? '👤' : '🤖';

    const bubble = document.createElement('div');
    bubble.className = 'bubble';

    // Simple formatting for bold text and line breaks
    // Ideally use a Markdown library here
    let formatted = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold
        .replace(/\n/g, '<br>'); // Newlines

    bubble.innerHTML = formatted;

    // Order depends on sender (check css) - but flex-direction handles it
    div.appendChild(avatar);
    div.appendChild(bubble);

    messagesContainer.appendChild(div);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

async function sendMessage(text) {
    if (!text.trim()) return;

    // UI Update
    addMessage(text, 'user');
    userInput.value = '';
    loading.classList.remove('hidden');

    try {
        // Send to Backend
        // We accept the delay (cold start) here
        // Use relative path for Vercel deployment
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: text,
                history: chatHistory
            })
        });

        if (!response.ok) {
            let errorDetail = 'Network response was not ok';
            try {
                const errData = await response.json();
                errorDetail = errData.detail || errorDetail;
            } catch (e) { }
            throw new Error(errorDetail);
        }

        const data = await response.json();
        const botResponse = data.response;

        // UI Update
        addMessage(botResponse, 'bot');

        // Update History
        chatHistory.push({ role: 'user', content: text });
        chatHistory.push({ role: 'assistant', content: botResponse });

    } catch (error) {
        console.error('Error:', error);
        addMessage(`⚠️ Error: ${error.message}`, 'bot');
    } finally {
        loading.classList.add('hidden');
    }
}

// Event Listeners
sendBtn.addEventListener('click', () => {
    sendMessage(userInput.value);
});

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage(userInput.value);
    }
});

quickQuestions.forEach(btn => {
    btn.addEventListener('click', () => {
        const query = btn.getAttribute('data-query');
        sendMessage(query);
    });
});

// Mobile Sidebar Toggle
const sidebarToggleBtn = document.getElementById('sidebar-toggle-btn');
const closeSidebarBtn = document.getElementById('close-sidebar-btn');
const chatSidebar = document.getElementById('chat-sidebar');

if (sidebarToggleBtn && chatSidebar) {
    sidebarToggleBtn.addEventListener('click', () => {
        chatSidebar.classList.add('show');
    });
}

if (closeSidebarBtn && chatSidebar) {
    closeSidebarBtn.addEventListener('click', () => {
        chatSidebar.classList.remove('show');
    });
}

// File Upload Logic
const uploadBtn = document.getElementById('upload-btn-trigger');
const fileInput = document.getElementById('pdf-upload');

if (uploadBtn && fileInput) {
    uploadBtn.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', async (e) => {
        if (e.target.files.length === 0) return;

        const originalText = uploadBtn.innerHTML;
        uploadBtn.innerHTML = '<ion-icon name="hourglass-outline"></ion-icon> Uploading...';
        uploadBtn.style.opacity = '0.7';
        uploadBtn.disabled = true;

        const formData = new FormData();
        for (let file of e.target.files) {
            formData.append('files', file);
        }

        try {
            const res = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();

            if (res.ok) {
                alert('Success: ' + data.message);
                addMessage('I have processed your files. You can now ask questions about them.', 'bot');
            } else {
                alert('Error: ' + data.detail);
            }
        } catch (err) {
            alert('Upload failed: ' + err.message);
        } finally {
            uploadBtn.innerHTML = originalText;
            uploadBtn.style.opacity = '1';
            uploadBtn.disabled = false;
            fileInput.value = '';
        }
    });
}