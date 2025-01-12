function confirmDelete(url) {
    Swal.fire({
        title: '<h3>Are you sure?</h3>',
        html: '<p>This action cannot be undone.</p>',
        background: '#f7f5f4',
        showCloseButton: true,
        closeButtonHtml: '&times;',
        showCancelButton: true,
        showConfirmButton: true,
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        buttonsStyling: false,
        reverseButtons: true,
        customClass: {
            popup: 'minimal-popup',
            confirmButton: 'btn-confirm',
            cancelButton: 'btn-cancel',
            actions: 'center-buttons',
            closeButton: 'close-btn',
        },
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(url, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            })
            .then(() => location.reload())
            .catch((err) => console.error(err));
        }
    });
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', () => {
    const csrftoken = getCookie('csrftoken');
    const messageInput = document.getElementById('chat-message-input');
    const messageSubmit = document.getElementById('chat-message-submit');

    function sendMessage() {
        const message = messageInput.value;

        if (message.trim()) {
            fetch('', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 'body': message }),
            })
            .then(() => location.reload())
            .catch((err) => console.error(err));
        }
    }

    messageSubmit.onclick = sendMessage;

    messageInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            sendMessage();
        }
    });
});

