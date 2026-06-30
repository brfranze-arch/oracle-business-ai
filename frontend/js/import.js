function renderImport() {
    setPageTitle("Oracle Import AI");

    setContent(`
        <div class="card">
            <h2>📂 Oracle Import AI</h2>
            <p>Importa entrate da file CSV o Excel. Il sistema riconosce clienti, importi, metodi di pagamento e categorie.</p>

            <input id="importFile" type="file" accept=".csv,.xlsx,.xls">

            <button onclick="uploadRevenueFile()">Importa Entrate</button>
            <button onclick="loadImportHistory()">Storico Import</button>

            <div id="importResult"></div>
        </div>
    `);
}

async function uploadRevenueFile() {
    const companyId = getCompanyId();
    const fileInput = document.getElementById("importFile");

    if (!fileInput.files || fileInput.files.length === 0) {
        document.getElementById("importResult").innerHTML =
            `<div class="result">Seleziona un file CSV o Excel.</div>`;
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const res = await fetch(`${API}/api/import/revenues/${companyId}`, {
        method: "POST",
        headers: {
            Authorization: `Bearer ${token()}`
        },
        body: formData
    });

    const data = await res.json();

    if (data.error) {
        document.getElementById("importResult").innerHTML =
            `<div class="result">Errore: ${data.error}</div>`;
        return;
    }

    document.getElementById("importResult").innerHTML = `
        <div class="card">
            <h3>Import completato</h3>

            <div class="kpi-grid">
                <div class="kpi">
                    <div class="kpi-title">Righe processate</div>
                    <div class="kpi-value">${data.rows_processed}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Righe create</div>
                    <div class="kpi-value">${data.rows_created}</div>
                </div>
            </div>

            <div class="result">
                <h3>Errori</h3>
                ${
                    data.errors && data.errors.length > 0
                        ? data.errors.map(e => `<p>${e}</p>`).join("")
                        : "Nessun errore."
                }
            </div>
        </div>
    `;
}

async function loadImportHistory() {
    const companyId = getCompanyId();

    const data = await apiGet(`/api/import/history/${companyId}`);

    if (!Array.isArray(data)) {
        document.getElementById("importResult").innerHTML =
            `<div class="result">${data.error || "Errore storico import"}</div>`;
        return;
    }

    document.getElementById("importResult").innerHTML = `
        <div class="card">
            <h3>Storico Import</h3>
            ${
                data.length > 0
                    ? data.map(job => `
                        <div class="result">
                            <span class="badge ${job.status === "completed" ? "badge-green" : "badge-yellow"}">
                                ${job.status}
                            </span>
                            <b>${job.file_name}</b><br>
                            Tipo: ${job.import_type}<br>
                            Righe processate: ${job.rows_processed}<br>
                            Righe create: ${job.rows_created}<br>
                            Data: ${job.created_at}<br>
                            Errori: ${job.errors || "-"}
                        </div>
                    `).join("")
                    : "<p>Nessun import ancora presente.</p>"
            }
        </div>
    `;
}