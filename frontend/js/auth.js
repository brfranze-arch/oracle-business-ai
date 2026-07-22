const ENTERPRISE_ROLES = new Set(["superadmin", "admin", "marketplace_manager", "partner_manager", "support"]);

function normalizedRole(user) {
    return String((user && user.role) || "client").trim().toLowerCase();
}

function isEnterpriseRole(user) {
    return ENTERPRISE_ROLES.has(normalizedRole(user));
}

async function registerUser() {
    document.getElementById("authResult").innerHTML = `<div class="result">Registrazione in corso...</div>`;
    const params = new URLSearchParams({
        name: document.getElementById("registerName").value,
        email: document.getElementById("registerEmail").value,
        password: document.getElementById("registerPassword").value
    });
    try {
        const res = await fetch(`${API}/api/auth/register?${params}`, {method: "POST"});
        const data = await res.json();
        if (!res.ok || data.error) throw new Error(data.detail || data.error || `Errore ${res.status}`);
        localStorage.setItem("oracle_token", data.token);
        localStorage.setItem("oracle_user", JSON.stringify(data.user));
        document.getElementById("authResult").innerHTML = `<div class="result">Registrazione completata.</div>`;
        startApp();
    } catch (error) {
        document.getElementById("authResult").innerHTML = `<div class="result">Errore: ${error.message}</div>`;
    }
}

async function loginUser() {
    document.getElementById("authResult").innerHTML = `<div class="result">Login in corso...</div>`;
    const params = new URLSearchParams({
        email: document.getElementById("loginEmail").value,
        password: document.getElementById("loginPassword").value
    });
    try {
        const res = await fetch(`${API}/api/auth/login?${params}`, {method: "POST"});
        const data = await res.json();
        if (!res.ok || data.error) throw new Error(data.detail || data.error || `Errore ${res.status}`);
        localStorage.setItem("oracle_token", data.token);
        localStorage.setItem("oracle_user", JSON.stringify(data.user));
        document.getElementById("authResult").innerHTML = `<div class="result">Login completato.</div>`;
        startApp();
    } catch (error) {
        document.getElementById("authResult").innerHTML = `<div class="result">Errore: ${error.message}</div>`;
    }
}

function logoutUser(message = "Logout completato.") {
    localStorage.removeItem("oracle_token");
    localStorage.removeItem("oracle_user");
    localStorage.removeItem("enterprise_permissions");
    document.getElementById("app").classList.add("hidden");
    document.getElementById("loginPage").classList.remove("hidden");
    document.getElementById("authResult").innerHTML = `<div class="result">${message}</div>`;
}

async function refreshEnterpriseAccess() {
    const user = JSON.parse(localStorage.getItem("oracle_user") || "null");
    if (!isEnterpriseRole(user)) {
        localStorage.removeItem("enterprise_permissions");
        return {authorized: false};
    }
    try {
        const res = await fetch(`${API}/api/enterprise-admin/access`, {headers: authHeaders()});
        const data = await res.json();
        if (!res.ok || !data.authorized) throw new Error(data.detail || "Accesso Enterprise non autorizzato");
        localStorage.setItem("enterprise_permissions", JSON.stringify(data.permissions || []));
        localStorage.setItem("oracle_user", JSON.stringify(data.user));
        return data;
    } catch (error) {
        console.warn("Verifica Enterprise:", error.message);
        return {authorized: false, error: error.message};
    }
}

async function startApp() {
    const user = JSON.parse(localStorage.getItem("oracle_user") || "null");
    document.getElementById("loginPage").classList.add("hidden");
    document.getElementById("app").classList.remove("hidden");
    if (user) {
        const role = normalizedRole(user).toUpperCase();
        document.getElementById("userInfo").innerText = `Connesso come ${user.name} — ${user.email} — ${role}`;
    }
    renderDashboard();
    refreshUserInfo();
    loadTenantSelector();
    const access = await refreshEnterpriseAccess();
    if (access.authorized && access.user) {
        document.getElementById("userInfo").innerText = `Connesso come ${access.user.name} — ${access.user.email} — ${access.user.role.toUpperCase()}`;
    }
}

window.addEventListener("load", function () {
    if (localStorage.getItem("oracle_token")) startApp();
    else {
        document.getElementById("loginPage").classList.remove("hidden");
        document.getElementById("app").classList.add("hidden");
    }
});
