function renderSettings() {
    setPageTitle("Settings");

    const userRaw = localStorage.getItem("oracle_user");
    const user = userRaw ? JSON.parse(userRaw) : null;

    setContent(`
        <div class="card">
            <h2>⚙️ Settings</h2>
            <p>Gestione account, aziende e configurazioni base.</p>

            <div class="grid-2">
                <div>
                    <h3>👤 Utente</h3>
                    <div class="result">
                        Nome: <b>${safeValue(user?.name)}</b><br>
                        Email: ${safeValue(user?.email)}<br>
                        Ruolo: ${safeValue(user?.role)}
                    </div>
                </div>

                <div>
                    <h3>🏢 Crea azienda</h3>
                    <input id="settingsCompanyName" placeholder="Nome azienda">
                    <input id="settingsSector" placeholder="Settore">
                    <input id="settingsCountry" placeholder="Paese">
                    <input id="settingsDomain" placeholder="Dominio aziendale">
                    <button onclick="createCompanyFromSettings()">Crea azienda</button>
                </div>
            </div>

            <hr>

            <button onclick="loadCompaniesSettings()">Carica aziende</button>

            <div id="settingsResult"></div>
        </div>
    `);
}

async function createCompanyFromSettings() {
    const params = new URLSearchParams({
        name: document.getElementById("settingsCompanyName").value || "Nuova azienda",
        sector: document.getElementById("settingsSector").value || "generale",
        country: document.getElementById("settingsCountry").value || "Italia",
        domain: document.getElementById("settingsDomain").value || ""
    });

    const res = await fetch(`${API}/api/companies?${params}`, {
        method: "POST",
        headers: authHeaders()
    });

    const data = await res.json();

    if (data.error) {
        showError("settingsResult", data.error);
        return;
    }

    document.getElementById("globalCompanyId").value = data.id;

    document.getElementById("settingsResult").innerHTML = `
        <div class="result">
            Azienda creata.<br>
            ID: <b>${safeValue(data.id)}</b><br>
            Nome: ${safeValue(data.name)}<br>
            Dominio: ${safeValue(data.domain)}
        </div>
    `;
}

async function loadCompaniesSettings() {
    const data = await apiGet("/api/companies");

    if (data.error) {
        showError("settingsResult", data.error);
        return;
    }

    const companies = safeArray(data);

    document.getElementById("settingsResult").innerHTML = `
        <div class="card">
            <h3>Aziende disponibili</h3>
            ${
                companies.length > 0
                    ? companies.map(c => `
                        <div class="result">
                            <span class="badge badge-blue">ID ${safeValue(c.id)}</span>
                            <b>${safeValue(c.name)}</b><br>
                            Settore: ${safeValue(c.sector)}<br>
                            Paese: ${safeValue(c.country)}<br>
                            Dominio: ${safeValue(c.domain)}<br><br>
                            <button onclick="selectCompany(${c.id})">
                                Usa questa azienda
                            </button>
                        </div>
                    `).join("")
                    : "<p>Nessuna azienda presente.</p>"
            }
        </div>
    `;
}

function selectCompany(id) {
    document.getElementById("globalCompanyId").value = id;

    document.getElementById("settingsResult").innerHTML += `
        <div class="result">
            Azienda selezionata: <b>ID ${id}</b>
        </div>
    `;
}