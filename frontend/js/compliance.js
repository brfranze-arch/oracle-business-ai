function renderCompliance() {
    setPageTitle("Compliance Oracle AI");

    setContent(`
        <div class="card">
            <h2>📄 Compliance Oracle AI</h2>
            <p>Gestione GDPR, scadenze, documenti, licenze e assicurazioni.</p>

            <div class="grid-2">
                <div>
                    <h3>Aggiungi elemento compliance</h3>
                    <input id="complianceTitle" placeholder="Titolo">
                    <input id="complianceType" placeholder="Tipo: GDPR, sicurezza, licenza, assicurazione">
                    <select id="complianceStatus">
                        <option value="completato">Completato</option>
                        <option value="pendente">Pendente</option>
                    </select>
                    <input id="complianceDueDate" placeholder="Scadenza YYYY-MM-DD">
                    <textarea id="complianceNotes" placeholder="Note"></textarea>
                    <button onclick="createComplianceItem()">Aggiungi elemento</button>
                </div>

                <div>
                    <h3>Analisi compliance</h3>
                    <button onclick="loadComplianceItems()">Carica elementi</button>
                    <button onclick="analyzeComplianceAi()">Analizza Compliance AI</button>
                    <button onclick="loadComplianceInsights()">Carica insights</button>
                </div>
            </div>

            <div id="complianceResult"></div>
        </div>
    `);
}

async function createComplianceItem() {
    const companyId = getCompanyId();

    const params = new URLSearchParams({
        company_id: companyId,
        title: document.getElementById("complianceTitle").value,
        item_type: document.getElementById("complianceType").value,
        status: document.getElementById("complianceStatus").value,
        due_date: document.getElementById("complianceDueDate").value,
        notes: document.getElementById("complianceNotes").value
    });

    const res = await fetch(`${API}/api/compliance-items?${params}`, {
        method: "POST",
        headers: authHeaders()
    });

    const data = await res.json();

    document.getElementById("complianceResult").innerHTML = `
        <div class="result">
            Elemento compliance creato.<br>
            ID: <b>${data.id}</b><br>
            Titolo: ${data.title}<br>
            Stato: ${data.status}<br>
            Scadenza: ${data.due_date || "-"}
        </div>
    `;
}

async function loadComplianceItems() {
    const companyId = getCompanyId();
    const data = await apiGet(`/api/compliance-items/${companyId}`);

    if (!Array.isArray(data)) {
        document.getElementById("complianceResult").innerHTML =
            `<div class="result">${data.error || "Errore caricamento compliance"}</div>`;
        return;
    }

    document.getElementById("complianceResult").innerHTML = `
        <div class="card">
            <h3>Elementi Compliance</h3>
            ${
                data.length > 0
                    ? data.map(item => `
                        <div class="result">
                            <span class="badge ${item.status === "completato" ? "badge-green" : "badge-yellow"}">
                                ${item.status}
                            </span>
                            <b>${item.title}</b><br>
                            Tipo: ${item.item_type}<br>
                            Scadenza: ${item.due_date || "-"}<br>
                            Note: ${item.notes || "-"}
                        </div>
                    `).join("")
                    : "<p>Nessun elemento compliance registrato.</p>"
            }
        </div>
    `;
}

async function analyzeComplianceAi() {
    const companyId = getCompanyId();
    const data = await apiPost(`/api/compliance-ai/${companyId}`);

    if (data.error) {
        document.getElementById("complianceResult").innerHTML =
            `<div class="result">${data.error}</div>`;
        return;
    }

    document.getElementById("complianceResult").innerHTML = `
        <div class="card">
            <h3>Compliance Oracle AI</h3>

            <span class="badge ${badgeClass(data.level)}">${data.level}</span>

            <div class="kpi-value">${data.compliance_score}/100</div>
            ${progressBar(data.compliance_score)}

            <div class="kpi-grid">
                <div class="kpi">
                    <div class="kpi-title">Elementi totali</div>
                    <div class="kpi-value">${data.total_items}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Completati</div>
                    <div class="kpi-value">${data.completed_items}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Pendenti</div>
                    <div class="kpi-value">${data.pending_items}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Scaduti</div>
                    <div class="kpi-value">${data.expired_items}</div>
                </div>
            </div>

            <div class="result">
                <h3>Analisi AI</h3>
                <p>${data.message}</p>
            </div>

            <div class="result">
                <h3>Raccomandazione</h3>
                <p>${data.recommendation}</p>
            </div>
        </div>
    `;
}

async function loadComplianceInsights() {
    const companyId = getCompanyId();
    const data = await apiGet(`/api/compliance-insights/${companyId}`);

    if (!Array.isArray(data)) {
        document.getElementById("complianceResult").innerHTML =
            `<div class="result">${data.error || "Errore caricamento insights"}</div>`;
        return;
    }

    document.getElementById("complianceResult").innerHTML = `
        <div class="card">
            <h3>Compliance Insights salvati</h3>
            ${
                data.length > 0
                    ? data.map(i => `
                        <div class="result">
                            <span class="badge ${badgeClass(i.level)}">${i.level}</span>
                            <b>Compliance Score: ${i.compliance_score}/100</b><br>
                            Elementi: ${i.total_items}<br>
                            Completati: ${i.completed_items}<br>
                            Pendenti: ${i.pending_items}<br>
                            Scaduti: ${i.expired_items}<br>
                            Creato il: ${i.created_at}<br><br>
                            <b>Messaggio:</b>
                            <p>${i.message}</p>
                            <b>Raccomandazione:</b>
                            <p>${i.recommendation}</p>
                        </div>
                    `).join("")
                    : "<p>Nessun insight compliance ancora presente.</p>"
            }
        </div>
    `;
}