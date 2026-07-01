function showPage(page, clickedButton = null) {
    document.querySelectorAll(".nav-btn").forEach(btn => {
        btn.classList.remove("active");
    });

    if (clickedButton) {
        clickedButton.classList.add("active");
    }

    if (page === "dashboard") renderDashboard();
    else if (page === "finance") renderFinance();
    else if (page === "customer") renderCustomer();
    else if (page === "compliance") renderCompliance();
    else if (page === "cyber") renderCyber();
    else if (page === "assistant") renderAssistant();
    else if (page === "import") renderImport();
    else if (page === "reports") renderReports();
    else if (page === "settings") renderSettings();
}

function getCompanyId() {
    return document.getElementById("globalCompanyId").value || "1";
}

function safeValue(value, fallback = "N/D") {
    if (value === undefined || value === null || value === "" || Number.isNaN(value)) {
        return fallback;
    }

    return value;
}

function safeNumber(value, fallback = 0) {
    const n = Number(value);
    return Number.isFinite(n) ? n : fallback;
}

function safeArray(value) {
    return Array.isArray(value) ? value : [];
}

function badgeClass(level) {
    const l = safeValue(level, "").toUpperCase();

    if (["ECCELLENTE", "FORTE", "OTTIMO", "BUONO"].includes(l)) return "badge-green";
    if (l === "STABILE") return "badge-blue";
    if (["FRAGILE", "ATTENZIONE"].includes(l)) return "badge-yellow";

    return "badge-red";
}

function severityBadge(severity) {
    const s = safeValue(severity, "").toLowerCase();

    if (s === "critical" || s === "critico") return "badge-red";
    if (s === "high" || s === "alto") return "badge-red";
    if (s === "medium" || s === "medio") return "badge-yellow";
    if (s === "low" || s === "basso") return "badge-blue";

    return "badge-blue";
}

function progressBar(value) {
    const safe = Math.max(0, Math.min(100, safeNumber(value)));

    return `
        <div class="progress-wrap">
            <div class="progress-bar" style="width:${safe}%"></div>
        </div>
    `;
}

function setPageTitle(title) {
    document.getElementById("pageTitle").innerText = title;
}

function setContent(html) {
    document.getElementById("pageContent").innerHTML = html;
}

function showError(targetId, message) {
    document.getElementById(targetId).innerHTML = `
        <div class="result">
            ${message || "Errore imprevisto."}
        </div>
    `;
}

function refreshUserInfo() {
    const userRaw = localStorage.getItem("oracle_user");
    const userInfo = document.getElementById("userInfo");

    if (!userRaw) {
        userInfo.innerText = "";
        return;
    }

    const user = JSON.parse(userRaw);
    userInfo.innerText = `Connesso come ${user.name} — ${user.email}`;
}