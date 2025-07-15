document.addEventListener("DOMContentLoaded", () => {
  const messagesDiv = document.getElementById("messages");
  const chatForm = document.getElementById("chatForm");
  const messageInput = document.getElementById("messageInput");

  // Fetch and display last 50 messages
  function loadMessages() {
    fetch("/get_messages")
      .then(res => res.json())
      .then(data => {
        messagesDiv.innerHTML = "";
        data.messages.forEach(msg => {
          const msgElem = document.createElement("div");
          msgElem.className = "mb-2";
          msgElem.innerHTML = `<strong>${escapeHtml(msg.user)}:</strong> ${escapeHtml(msg.message)} <span class="text-gray-400 text-xs">(${msg.timestamp})</span>`;
          messagesDiv.appendChild(msgElem);
        });
        // Scroll to bottom after loading
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
      })
      .catch(err => {
        console.error("Failed to load messages:", err);
      });
  }

  // Escape to prevent XSS
  function escapeHtml(text) {
    return text.replace(/[&<>"']/g, m => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;"
    })[m]);
  }

  // Send new message
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

  // Get CSRF token from cookies
  function getCSRFToken() {
    let cookieValue = null;
    const name = "csrftoken";
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // Initial load
  loadMessages();

  // Optional: poll for new messages every 5 seconds
  setInterval(loadMessages, 5000);
});
