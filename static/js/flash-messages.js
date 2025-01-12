document.addEventListener("DOMContentLoaded", () => {
    const messages = document.querySelectorAll(".messages .message");
    messages.forEach((message) => {
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            message.style.opacity = "0";
            message.style.transition = "opacity 0.5s";
            setTimeout(() => message.remove(), 500);
        }, 5000);

        // Manual dismiss on button click
        const closeButton = message.querySelector("button");
        if (closeButton) {
            closeButton.addEventListener("click", () => {
                message.style.display = "none";
            });
        }
    });
});
