function renderSettings() {
    setPageTitle("Settings");

    const userRaw = localStorage.getItem("oracle_user");
    const user = userRaw ? JSON.parse(userRaw) : null;

    setContent(`
        <div class="card">
            <h2>⚙️ Settings</h2>
            <p>Gestione account, azienda e configurazioni base.</p>

            <div class="grid-2">
                <div>
                    <h3>👤 Utente</h3>
                    <div class="result">
                        Nome: <b>${user ? user.name : "-"}</b><br>
                        Email: ${user ? user.email : "-"}<br>
                        Ruolo: ${user ? user.role : "-"}
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
        name: document.getElementById("settingsCompanyName").value,
        sector: document.getElementById("settingsSector").value,
        country: document.getElementById("settingsCountry").value,
        domain: document.getElementById("settingsDomain").value
    });

    const res = await fetch(`${API}/api/companies?${params}`, {
        method: "POST",
        headers: authHeaders()
    });

    const data = await res.json();

    if (data.error) {
        document.getElementById("settingsResult").innerHTML =
            `<div class="result">${data.error}</div>`;
        return;
    }

    document.getElementById("globalCompanyId").value = data.id;

    document.getElementById("settingsResult").innerHTML = `
        <div class="result">
            Azienda creata.<br>
            ID: <b>${data.id}</b><br>
            Nome: ${data.name}<br>
            Dominio: ${data.domain || "-"}
        </div>
    `;
}

async function loadCompaniesSettings() {
    const data = await apiGet("/api/companies");

    if (!Array.isArray(data)) {
        document.getElementById("settingsResult").innerHTML =
            `<div class="result">${data.error || "Errore caricamento aziende"}</div>`;
        return;
    }

    document.getElementById("settingsResult").innerHTML = `
        <div class="card">
            <h3>Aziende disponibili</h3>
            ${
                data.length > 0
                    ? data.map(c => `
                        <div class="result">
                            <span class="badge badge-blue">ID ${c.id}</span>
                            <b>${c.name}</b><br>
                            Settore: ${c.sector || "-"}<br>
                            Paese: ${c.country || "-"}<br>
                            Dominio: ${c.domain || "-"}<br><br>
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