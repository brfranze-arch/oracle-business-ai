async function registerUser() {
    document.getElementById("authResult").innerHTML =
        `<div class="result">Registrazione in corso...</div>`;

    const params = new URLSearchParams({
        name: document.getElementById("registerName").value,
        email: document.getElementById("registerEmail").value,
        password: document.getElementById("registerPassword").value
    });

    const res = await fetch(`${API}/api/auth/register?${params}`, {
        method: "POST"
    });

    const data = await res.json();

    if (data.error) {
        document.getElementById("authResult").innerHTML =
            `<div class="result">Errore: ${data.error}</div>`;
        return;
    }

    localStorage.setItem("oracle_token", data.token);
    localStorage.setItem("oracle_user", JSON.stringify(data.user));

    document.getElementById("authResult").innerHTML =
        `<div class="result">Registrazione completata. Accesso in corso...</div>`;

    startApp();
}

async function loginUser() {
    document.getElementById("authResult").innerHTML =
        `<div class="result">Login in corso...</div>`;

    const params = new URLSearchParams({
        email: document.getElementById("loginEmail").value,
        password: document.getElementById("loginPassword").value
    });

    const res = await fetch(`${API}/api/auth/login?${params}`, {
        method: "POST"
    });

    const data = await res.json();

    if (data.error) {
        document.getElementById("authResult").innerHTML =
            `<div class="result">Errore: ${data.error}</div>`;
        return;
    }

    localStorage.setItem("oracle_token", data.token);
    localStorage.setItem("oracle_user", JSON.stringify(data.user));

    document.getElementById("authResult").innerHTML =
        `<div class="result">Login completato.</div>`;

    startApp();
}

function logoutUser() {
    localStorage.removeItem("oracle_token");
    localStorage.removeItem("oracle_user");

    document.getElementById("app").classList.add("hidden");
    document.getElementById("loginPage").classList.remove("hidden");

    document.getElementById("authResult").innerHTML =
        `<div class="result">Logout completato.</div>`;
}

function startApp() {
    const userRaw = localStorage.getItem("oracle_user");

    document.getElementById("loginPage").classList.add("hidden");
    document.getElementById("app").classList.remove("hidden");

    if (userRaw) {
        const user = JSON.parse(userRaw);
        document.getElementById("userInfo").innerText =
            `Connesso come ${user.name} — ${user.email}`;
    }

    renderDashboard();
}

window.addEventListener("load", function () {
    const savedToken = localStorage.getItem("oracle_token");

    if (savedToken) {
        startApp();
    } else {
        document.getElementById("loginPage").classList.remove("hidden");
        document.getElementById("app").classList.add("hidden");
    }
});