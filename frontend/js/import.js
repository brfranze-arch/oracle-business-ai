function renderImport() {
    setPageTitle("Oracle Import Enterprise");

    setContent(`
        <div class="card">
            <h2>📂 Oracle Import Enterprise</h2>

            <p>
                Importa un intero ambiente aziendale da un solo
                file Excel multi-foglio.
            </p>

            <div class="result">
                <h3>Fogli riconosciuti</h3>

                <span class="badge badge-blue">Customers</span>
                <span class="badge badge-blue">Revenues</span>
                <span class="badge badge-blue">Compliance</span>
                <span class="badge badge-blue">CyberAssets</span>
                <span class="badge badge-blue">CyberFindings</span>
                <span class="badge badge-blue">Threats</span>
                <span class="badge badge-blue">PredictiveHistory</span>
                <span class="badge badge-blue">AgentsHistory</span>

                <p>
                    L'import legge automaticamente tutti i fogli
                    presenti e ignora quelli non riconosciuti.
                </p>
            </div>

            <input
                id="enterpriseImportFile"
                type="file"
                accept=".xlsx,.xls"
            >

            <button onclick="uploadEnterpriseWorkbook()">
                Importa intero file Excel
            </button>

            <button onclick="loadImportHistory()">
                Storico Import
            </button>

            <div id="importResult"></div>
        </div>
    `);
}


async function uploadEnterpriseWorkbook() {
    const companyId = getCompanyId();
    const input = document.getElementById(
        "enterpriseImportFile"
    );

    if (!input.files || input.files.length === 0) {
        showError(
            "importResult",
            "Seleziona un file Excel .xlsx o .xls."
        );
        return;
    }

    const file = input.files[0];

    if (
        !file.name.toLowerCase().endsWith(".xlsx") &&
        !file.name.toLowerCase().endsWith(".xls")
    ) {
        showError(
            "importResult",
            "Il file deve essere in formato Excel."
        );
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    document.getElementById("importResult").innerHTML = `
        <div class="card">
            <h3>⏳ Import Enterprise in corso</h3>
            <p>
                Lettura fogli, validazione dati e creazione record...
            </p>
        </div>
    `;

    try {
        const response = await fetch(
            `${API}/api/import/enterprise/${companyId}`,
            {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${token()}`,
                    "X-Tenant-Id": getTenantId()
                },
                body: formData
            }
        );

        const data = await response.json();

        if (data.error) {
            showError("importResult", data.error);
            return;
        }

        renderEnterpriseImportResult(data);

    } catch (error) {
        console.error(error);

        showError(
            "importResult",
            "Errore di connessione durante l'import."
        );
    }
}


function renderEnterpriseImportResult(data) {
    const modules = data.modules || {};

    const moduleCards = Object.entries(modules)
        .map(([moduleName, moduleData]) => {
            const errors = safeArray(moduleData.errors);
            const skipped = moduleData.skipped === true;

            return `
                <div class="result">
                    <span class="badge ${
                        skipped
                            ? "badge-yellow"
                            : errors.length > 0
                                ? "badge-yellow"
                                : "badge-green"
                    }">
                        ${
                            skipped
                                ? "SKIPPED"
                                : errors.length > 0
                                    ? "WARNING"
                                    : "OK"
                        }
                    </span>

                    <h3>${safeValue(moduleName)}</h3>

                    Processati:
                    <b>${safeNumber(moduleData.processed)}</b>
                    <br>

                    Creati:
                    <b>${safeNumber(moduleData.created)}</b>
                    <br>

                    Aggiornati:
                    <b>${safeNumber(moduleData.updated)}</b>
                    <br>

                    ${
                        moduleData.message
                            ? `
                                <p>
                                    ${safeValue(moduleData.message)}
                                </p>
                            `
                            : ""
                    }

                    ${
                        errors.length > 0
                            ? `
                                <details>
                                    <summary>
                                        Mostra ${errors.length} errori
                                    </summary>

                                    ${errors.map(error => `
                                        <p>${safeValue(error)}</p>
                                    `).join("")}
                                </details>
                            `
                            : ""
                    }
                </div>
            `;
        })
        .join("");

    document.getElementById("importResult").innerHTML = `
        <div class="card">
            <h2>✅ Import Enterprise completato</h2>

            <div class="kpi-grid">
                <div class="kpi">
                    <div class="kpi-title">
                        Righe processate
                    </div>
                    <div class="kpi-value">
                        ${safeNumber(data.total_processed)}
                    </div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">
                        Record creati
                    </div>
                    <div class="kpi-value">
                        ${safeNumber(data.total_created)}
                    </div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">
                        Record aggiornati
                    </div>
                    <div class="kpi-value">
                        ${safeNumber(data.total_updated)}
                    </div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">
                        Errori
                    </div>
                    <div class="kpi-value">
                        ${safeNumber(data.total_errors)}
                    </div>
                </div>
            </div>

            <div class="result">
                <h3>File importato</h3>
                <p>${safeValue(data.file_name)}</p>

                <h3>Fogli trovati</h3>
                <p>
                    ${safeArray(data.available_sheets)
                        .map(sheet => `
                            <span class="badge badge-blue">
                                ${safeValue(sheet)}
                            </span>
                        `)
                        .join("")}
                </p>
            </div>

            ${moduleCards}

            <div class="result">
                <h3>Test consigliati</h3>

                <p>
                    Apri Finance e verifica le entrate.
                </p>

                <p>
                    Apri Customer e verifica i clienti.
                </p>

                <p>
                    Apri Compliance e verifica gli elementi.
                </p>

                <p>
                    Apri Cyber e carica Asset, Finding e Threat.
                </p>

                <p>
                    Apri Reports e verifica Predictive e Agents.
                </p>
            </div>
        </div>
    `;
}


async function loadImportHistory() {
    const companyId = getCompanyId();

    const data = await apiGet(
        `/api/import/history/${companyId}`
    );

    if (data.error) {
        showError("importResult", data.error);
        return;
    }

    const jobs = safeArray(data);

    document.getElementById("importResult").innerHTML = `
        <div class="card">
            <h3>📋 Storico Import</h3>

            ${
                jobs.length > 0
                    ? jobs.map(job => `
                        <div class="result">
                            <span class="badge ${
                                job.status === "completed"
                                    ? "badge-green"
                                    : "badge-yellow"
                            }">
                                ${safeValue(job.status)}
                            </span>

                            <b>${safeValue(job.file_name)}</b>
                            <br>

                            Tipo:
                            ${safeValue(job.import_type)}
                            <br>

                            Righe processate:
                            ${safeNumber(job.rows_processed)}
                            <br>

                            Record creati:
                            ${safeNumber(job.rows_created)}
                            <br>

                            Data:
                            ${safeValue(job.created_at)}
                            <br>

                            ${
                                job.errors
                                    ? `
                                        <details>
                                            <summary>
                                                Visualizza errori
                                            </summary>
                                            <pre style="
                                                white-space:pre-wrap;
                                                font-family:inherit;
                                            ">${safeValue(job.errors)}</pre>
                                        </details>
                                    `
                                    : ""
                            }
                        </div>
                    `).join("")
                    : `
                        <p>
                            Nessun import presente.
                        </p>
                    `
            }
        </div>
    `;
}