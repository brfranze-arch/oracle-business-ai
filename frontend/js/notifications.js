function buildNotifications(data) {
    const notifications = [];

    if (data.oracle_score < 65) {
        notifications.push({ type: "warning", icon: "⚠️", text: "Oracle Score sotto la soglia FORTE." });
    }

    if (data.attack_probability_30d > 25) {
        notifications.push({ type: "danger", icon: "🛡", text: `Rischio cyber 30 giorni: ${data.attack_probability_30d}%.` });
    }

    if (data.risks && data.risks.length > 0) {
        notifications.push({ type: "warning", icon: "🚨", text: `${data.risks.length} rischi aziendali rilevati.` });
    }

    if (data.suggestions && data.suggestions.length > 0) {
        notifications.push({ type: "info", icon: "🤖", text: `${data.suggestions.length} azioni AI consigliate.` });
    }

    if (notifications.length === 0) {
        notifications.push({ type: "success", icon: "✅", text: "Nessuna criticità importante rilevata." });
    }

    return notifications;
}

function renderNotificationCenter(notifications) {
    const box = document.getElementById("notificationBox");
    const count = document.getElementById("notificationCount");

    if (!box || !count) return;

    const list = Array.isArray(notifications) ? notifications : [];
    count.innerText = list.length;

    box.innerHTML = `
        <div class="notification-header-v2">
            <strong>Oracle Notifications</strong>
            <small>${new Date().toLocaleString("it-IT")}</small>
        </div>
        ${list.map(n => `
            <div class="notification-item ${n.type}">
                <span>${n.icon}</span>
                <p>${n.text}</p>
            </div>
        `).join("")}
    `;
}

function toggleNotifications() {
    const panel = document.getElementById("notificationPanel");
    if (!panel) return;
    panel.classList.toggle("hidden");
}
