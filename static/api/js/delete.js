import { getCookie } from './utils.js';

async function confirmDelete(url) {
    const result = await Swal.fire({
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
    });

    if (result.isConfirmed) {
        try {
            await fetch(url, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            });

            // Remove the deleted message without reloading the page
            const messageDiv = document.querySelector(`[data-url="${url}"]`).closest('[data-type="deletable-item"]');
            if (messageDiv) {
                messageDiv.remove();
            }
        } catch (err) {
            console.error('Error while deleting:', err);
        }
    }
}

// Event delegation: Add the listener to the parent container
document.querySelector('[data-role="feed-container"]').addEventListener('click', (event) => {
    if (event.target.classList.contains('delete-button')) {
        const url = event.target.dataset.url;
        confirmDelete(url);
    }
});
