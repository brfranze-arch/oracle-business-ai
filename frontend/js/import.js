function renderImport() {
    setPageTitle("Oracle Import AI");

    setContent(`
        <div class="card">
            <h2>📂 Oracle Import AI</h2>
            <p>Importa entrate da CSV o Excel. Il sistema riconosce clienti, importi, metodi e categorie.</p>

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
        showError("importResult", "Seleziona un file CSV o Excel.");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
        const res = await fetch(`${API}/api/import/revenues/${companyId}`, {
            method: "POST",
            headers: {
                Authorization: `Bearer ${token()}`
            },
            body: formData
        });

        const data = await res.json();

        if (data.error) {
            showError("importResult", data.error);
            return;
        }

        document.getElementById("importResult").innerHTML = `
            <div class="card">
                <h3>Import completato</h3>

                <div class="kpi-grid">
                    <div class="kpi">
                        <div class="kpi-title">Righe processate</div>
                        <div class="kpi-value">${safeNumber(data.rows_processed)}</div>
                    </div>

                    <div class="kpi">
                        <div class="kpi-title">Righe create</div>
                        <div class="kpi-value">${safeNumber(data.rows_created)}</div>
                    </div>
                </div>

                <div class="result">
                    <h3>Errori</h3>
                    ${
                        safeArray(data.errors).length > 0
                            ? safeArray(data.errors).map(e => `<p>${safeValue(e)}</p>`).join("")
                            : "Nessun errore."
                    }
                </div>
            </div>
        `;
    } catch (e) {
        showError("importResult", "Errore durante l’upload del file.");
    }
}

async function loadImportHistory() {
    const companyId = getCompanyId();
    const data = await apiGet(`/api/import/history/${companyId}`);

    if (data.error) {
        showError("importResult", data.error);
        return;
    }

    const jobs = safeArray(data);

    document.getElementById("importResult").innerHTML = `
        <div class="card">
            <h3>Storico Import</h3>
            ${
                jobs.length > 0
                    ? jobs.map(job => `
                        <div class="result">
                            <span class="badge ${job.status === "completed" ? "badge-green" : "badge-yellow"}">
                                ${safeValue(job.status)}
                            </span>
                            <b>${safeValue(job.file_name)}</b><br>
                            Tipo: ${safeValue(job.import_type)}<br>
                            Righe processate: ${safeNumber(job.rows_processed)}<br>
                            Righe create: ${safeNumber(job.rows_created)}<br>
                            Data: ${safeValue(job.created_at)}<br>
                            Errori: ${safeValue(job.errors, "-")}
                        </div>
                    `).join("")
                    : "<p>Nessun import presente.</p>"
            }
        </div>
    `;
}