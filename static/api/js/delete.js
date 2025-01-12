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
            location.reload();
        } catch (err) {
            console.error(err);
        }
    }
}

document.querySelectorAll('.delete-button').forEach(button => {
    button.addEventListener('click', (event) => {
        const url = event.target.dataset.url;
        confirmDelete(url);
    });
});

