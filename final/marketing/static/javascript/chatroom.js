document.addEventListener("DOMContentLoaded", () => {
    const messagesDiv = document.getElementById("messages");
    const chatForm = document.getElementById("chatForm");
    const messageInput = document.getElementById("messageInput");

    //retrieve last 50 messages
    function loadMessages() {
        fetch("/get_messages")
        .then(res => res.json())
        .then(data => {
            messagesDiv.innerHTML = ""; //clear previous messages

            data.messages.forEach(msg => {
            const msgElem = document.createElement("div");
            msgElem.className = "mb-2";

            const userSpan = document.createElement("strong");
            userSpan.textContent = `${msg.user}: `;

            const messageSpan = document.createElement("span");
            messageSpan.textContent = msg.message;

            const timestampSpan = document.createElement("span");
            timestampSpan.className = "text-gray-400 text-xs ml-2";
            timestampSpan.textContent = `(${msg.timestamp})`;

            msgElem.appendChild(userSpan);
            msgElem.appendChild(messageSpan);
            msgElem.appendChild(timestampSpan);

            messagesDiv.appendChild(msgElem);
            });

            //scroll to bottom after loading
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        })
        .catch(err => {
            console.error("Failed to load messages:", err);
        });
    }

    //send new message
    chatForm.addEventListener("submit", e => {
        e.preventDefault();
        const message = messageInput.value.trim();
        if (!message) return;

        const formData = new FormData();
        formData.append("message", message);

        fetch("/send_message", {
            method: "POST",
            body: formData,
            headers: {
            "X-CSRFToken": getCSRFToken()
            }
        })
        .then(res => res.json())
        .then(data => {
        if (data.success) {
            messageInput.value = "";
            loadMessages();
        } else {
            alert(data.error || "Failed to send message");
        }
        })
        .catch(err => {
            console.error("Error sending message:", err);
            alert("Error sending message");
        });
    });

    //get CSRF token from cookies
    function getCSRFToken() {
        return document.querySelector('[name=csrf-token]')?.getAttribute('content');
    }

    //initial load
    loadMessages();

    //check for new messages every 5 seconds
    setInterval(loadMessages, 5000);
});
