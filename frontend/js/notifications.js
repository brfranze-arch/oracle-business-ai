function buildNotifications(data) {
    const notifications = [];

    if (!data) {
        return [{ type: "info", icon: "ℹ️", text: "Notification Center in attesa dati." }];
    }

    if (Number(data.oracle_score || 0) < 65) {
        notifications.push({ type: "warning", icon: "⚠️", text: "Oracle Score sotto la soglia FORTE." });
    }

    if (Number(data.attack_probability_30d || 0) > 25) {
        notifications.push({ type: "danger", icon: "🛡", text: `Rischio cyber 30 giorni: ${data.attack_probability_30d}%.` });
    }

    if (Array.isArray(data.risks) && data.risks.length > 0) {
        notifications.push({ type: "warning", icon: "🚨", text: `${data.risks.length} rischi aziendali rilevati.` });
    }

    if (Array.isArray(data.suggestions) && data.suggestions.length > 0) {
        notifications.push({ type: "info", icon: "🤖", text: `${data.suggestions.length} azioni AI consigliate.` });
    }

    notifications.push({ type: "success", icon: "🟢", text: "Billing, Workspace e AI Engine operativi." });

    return notifications.slice(0, 8);
}

function renderNotificationCenter(notifications) {
    const box = document.getElementById("notificationBox");
    const count = document.getElementById("notificationCount");

    if (!box || !count) return;

    const list = Array.isArray(notifications) ? notifications : [];
    count.innerText = list.length;

    box.innerHTML = list.map(n => `
        <div class="notification-item ${n.type}">
            <span>${n.icon}</span>
            <p>${n.text}</p>
        </div>
    `).join("");
}

function toggleNotifications() {
    const panel = document.getElementById("notificationPanel");
    if (!panel) return;
    panel.classList.toggle("hidden");
}
