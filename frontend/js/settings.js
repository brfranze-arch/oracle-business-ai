function renderSettings() {
    setPageTitle("Impostazioni");

    const userRaw = localStorage.getItem("oracle_user");
    const user = userRaw ? JSON.parse(userRaw) : null;

    setContent(`
        <div class="card">
            <h2>⚙️ Impostazioni</h2>
            <p>Gestione account, workspace e aziende collegate al tenant selezionato.</p>

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
                    <h3>🏢 Crea azienda nel workspace</h3>
                    <input id="settingsCompanyName" placeholder="Nome azienda">
                    <input id="settingsSector" placeholder="Settore">
                    <input id="settingsCountry" placeholder="Paese">
                    <input id="settingsDomain" placeholder="Dominio aziendale">
                    <button onclick="createTenantCompany()">Crea azienda nel tenant</button>
                </div>
            </div>

            <hr>

            <div class="grid-2">
                <div>
                    <h3>🔗 Collega azienda esistente</h3>
                    <input id="existingCompanyId" placeholder="ID azienda esistente">
                    <button onclick="linkExistingCompanyToTenant()">Collega al tenant</button>
                </div>

                <div>
                    <h3>📋 Aziende del tenant</h3>
                    <button onclick="loadTenantCompanies()">Carica aziende workspace</button>
                </div>
            </div>

            <div id="settingsResult"></div>
        </div>
    `);
}

async function createTenantCompany() {
    const params = new URLSearchParams({
        name: document.getElementById("settingsCompanyName").value || "Nuova azienda",
        sector: document.getElementById("settingsSector").value || "generale",
        country: document.getElementById("settingsCountry").value || "Italia",
        domain: document.getElementById("settingsDomain").value || ""
    });

    const res = await fetch(`${API}/api/tenant/companies?${params}`, {
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
            Azienda creata nel tenant.<br>
            ID: <b>${safeValue(data.id)}</b><br>
            Nome: ${safeValue(data.name)}<br>
            Settore: ${safeValue(data.sector)}<br>
            Paese: ${safeValue(data.country)}<br>
            Dominio: ${safeValue(data.domain)}
        </div>
    `;
}

async function loadTenantCompanies() {
    const data = await apiGet("/api/tenant/companies");

    if (data.error) {
        showError("settingsResult", data.error);
        return;
    }

    const companies = safeArray(data);

    document.getElementById("settingsResult").innerHTML = `
        <div class="card">
            <h3>Aziende del workspace selezionato</h3>
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
                    : "<p>Nessuna azienda collegata a questo workspace.</p>"
            }
        </div>
    `;
}

async function linkExistingCompanyToTenant() {
    const companyId = document.getElementById("existingCompanyId").value;

    const params = new URLSearchParams({
        company_id: companyId
    });

    const res = await fetch(`${API}/api/tenant/link-company?${params}`, {
        method: "POST",
        headers: authHeaders()
    });

    const data = await res.json();

    if (data.error) {
        showError("settingsResult", data.error);
        return;
    }

    document.getElementById("settingsResult").innerHTML = `
        <div class="result">
            ${safeValue(data.message)}<br>
            Tenant ID: <b>${safeValue(data.tenant_id)}</b><br>
            Company ID: <b>${safeValue(data.company_id)}</b>
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