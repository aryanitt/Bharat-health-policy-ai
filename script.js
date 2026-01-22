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
            throw new Error('Network response was not ok');
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
        addMessage("⚠️ Sorry, I'm having trouble connecting to the server. (It might be waking up!)", 'bot');
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
