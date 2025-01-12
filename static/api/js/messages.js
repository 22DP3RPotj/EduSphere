import { getCookie } from './utils.js';

document.addEventListener('DOMContentLoaded', () => {
    const csrftoken = getCookie('csrftoken');
    const messageInput = document.getElementById('chat-message-input');
    const messageSubmit = document.getElementById('chat-message-submit');

    function sendMessage() {
        const message = messageInput.value.trim();
    
        if (!message) {
            return;
        }
    
        fetch('', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 'body': message }),
        })
        .then(() => {
            messageInput.value = '';
            location.reload();
        })
        .catch((err) => console.error(err));
    }
    

    messageSubmit.addEventListener('click', sendMessage);

    messageInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            sendMessage();
        }
    });
});

