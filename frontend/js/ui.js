function showPage(page, clickedButton = null) {
    document.querySelectorAll(".nav-btn").forEach(btn => {
        btn.classList.remove("active");
    });

    if (clickedButton) {
        clickedButton.classList.add("active");
    }

    if (page === "dashboard") renderDashboard();
    if (page === "finance") renderFinance();
    if (page === "customer") renderCustomer();
    if (page === "compliance") renderCompliance();
    if (page === "cyber") renderCyber();
    if (page === "assistant") renderAssistant();
    if (page === "import") renderImport();
    if (page === "settings") renderSettings();
    if (page === "reports") renderReports();
}

function getCompanyId() {
    return document.getElementById("globalCompanyId").value || "1";
}

function badgeClass(level) {
    if (["ECCELLENTE", "FORTE", "OTTIMO", "BUONO"].includes(level)) return "badge-green";
    if (level === "STABILE") return "badge-blue";
    if (["FRAGILE", "ATTENZIONE"].includes(level)) return "badge-yellow";
    return "badge-red";
}

function progressBar(value) {
    const safeValue = Math.max(0, Math.min(100, Number(value || 0)));

    return `
        <div class="progress-wrap">
            <div class="progress-bar" style="width:${safeValue}%"></div>
        </div>
    `;
}

function setPageTitle(title) {
    document.getElementById("pageTitle").innerText = title;
}

function setContent(html) {
    document.getElementById("pageContent").innerHTML = html;
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