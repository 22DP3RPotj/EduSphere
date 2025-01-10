function confirmDelete(roomId) {
    Swal.fire({
        title: 'Are you sure?',
        text: 'This action cannot be undone!',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#4CAF50',
        cancelButtonColor: '#FF5252',
        confirmButtonText: 'Yes, delete it!',
        cancelButtonText: 'Cancel',
        background: '#f2f2f2',
        color: '#333',
        customClass: {
            title: 'swal-title',
            text: 'swal-text',
            confirmButton: 'swal-confirm-button',
            cancelButton: 'swal-cancel-button'
        }
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`api/delete-room/${roomId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            })
            .then(response => {
                if (response.ok) {
                    Swal.fire('Deleted!', 'The room has been deleted.', 'success');
                    location.reload(); // Reload or update the UI as needed
                } else {
                    Swal.fire('Error!', 'Failed to delete the room.', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                Swal.fire('Error!', 'An unexpected error occurred.', 'error');
            });
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
