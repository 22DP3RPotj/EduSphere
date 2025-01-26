document.addEventListener("DOMContentLoaded", () => {
    const messages = document.querySelectorAll(".messages .message");
    messages.forEach((message) => {
        // Auto-dismiss after 3 seconds
        setTimeout(() => {
            message.style.opacity = "0";
            message.style.transition = "opacity 0.5s";
            setTimeout(() => message.remove(), 500);
        }, 3000);
    });
});
