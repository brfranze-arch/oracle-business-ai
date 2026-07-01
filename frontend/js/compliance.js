function renderCompliance() {
    setPageTitle("Compliance Oracle AI");

    setContent(`
        <div class="card">
            <h2>📄 Compliance Oracle AI</h2>
            <p>GDPR, scadenze, documenti, licenze, assicurazioni e compliance score.</p>

            <div class="grid-2">
                <div>
                    <h3>Aggiungi elemento</h3>
                    <input id="complianceTitle" placeholder="Titolo">
                    <input id="complianceType" placeholder="Tipo: GDPR, sicurezza, licenza">
                    <select id="complianceStatus">
                        <option value="completato">Completato</option>
                        <option value="pendente">Pendente</option>
                    </select>
                    <input id="complianceDueDate" placeholder="Scadenza YYYY-MM-DD">
                    <textarea id="complianceNotes" placeholder="Note"></textarea>
                    <button onclick="createComplianceItem()">Aggiungi elemento</button>
                </div>

                <div>
                    <h3>Azioni Compliance</h3>
                    <button onclick="loadComplianceItems()">Carica elementi</button>
                    <button onclick="analyzeComplianceAi()">Analisi Compliance AI</button>
                    <button onclick="loadComplianceInsights()">Insights salvati</button>
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
        title: document.getElementById("complianceTitle").value || "Elemento compliance",
        item_type: document.getElementById("complianceType").value || "generale",
        status: document.getElementById("complianceStatus").value || "pendente",
        due_date: document.getElementById("complianceDueDate").value || "",
        notes: document.getElementById("complianceNotes").value || ""
    });

    const res = await fetch(`${API}/api/compliance-items?${params}`, {
        method: "POST",
        headers: authHeaders()
    });

    const data = await res.json();

    if (data.error) {
        showError("complianceResult", data.error);
        return;
    }

    document.getElementById("complianceResult").innerHTML = `
        <div class="result">
            Elemento creato.<br>
            ID: <b>${safeValue(data.id)}</b><br>
            Titolo: ${safeValue(data.title)}<br>
            Stato: ${safeValue(data.status)}<br>
            Scadenza: ${safeValue(data.due_date)}
        </div>
    `;
}

async function loadComplianceItems() {
    const companyId = getCompanyId();
    const data = await apiGet(`/api/compliance-items/${companyId}`);

    if (data.error) {
        showError("complianceResult", data.error);
        return;
    }

    const items = safeArray(data);

    document.getElementById("complianceResult").innerHTML = `
        <div class="card">
            <h3>Elementi Compliance</h3>
            ${
                items.length > 0
                    ? items.map(item => `
                        <div class="result">
                            <span class="badge ${item.status === "completato" ? "badge-green" : "badge-yellow"}">
                                ${safeValue(item.status)}
                            </span>
                            <b>${safeValue(item.title)}</b><br>
                            Tipo: ${safeValue(item.item_type)}<br>
                            Scadenza: ${safeValue(item.due_date)}<br>
                            Note: ${safeValue(item.notes)}
                        </div>
                    `).join("")
                    : "<p>Nessun elemento compliance presente.</p>"
            }
        </div>
    `;
}

async function analyzeComplianceAi() {
    const companyId = getCompanyId();
    const data = await apiPost(`/api/compliance-ai/${companyId}`);

    if (data.error) {
        showError("complianceResult", data.error);
        return;
    }

    const score = safeNumber(data.compliance_score);
    const level = safeValue(data.level, "STABILE");

    document.getElementById("complianceResult").innerHTML = `
        <div class="card">
            <h3>Compliance Oracle AI</h3>

            <span class="badge ${badgeClass(level)}">${level}</span>

            <div class="kpi-value">${score}/100</div>
            ${progressBar(score)}

            <div class="kpi-grid">
                <div class="kpi">
                    <div class="kpi-title">Totali</div>
                    <div class="kpi-value">${safeNumber(data.total_items)}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Completati</div>
                    <div class="kpi-value">${safeNumber(data.completed_items)}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Pendenti</div>
                    <div class="kpi-value">${safeNumber(data.pending_items)}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Scaduti</div>
                    <div class="kpi-value">${safeNumber(data.expired_items)}</div>
                </div>
            </div>

            <div class="result">
                <h3>Analisi AI</h3>
                <p>${safeValue(data.message, "Nessuna analisi disponibile.")}</p>
            </div>

            <div class="result">
                <h3>Raccomandazione</h3>
                <p>${safeValue(data.recommendation, "Nessuna raccomandazione disponibile.")}</p>
            </div>
        </div>
    `;
}

async function loadComplianceInsights() {
    const companyId = getCompanyId();
    const data = await apiGet(`/api/compliance-insights/${companyId}`);

    if (data.error) {
        showError("complianceResult", data.error);
        return;
    }

    const insights = safeArray(data);

    document.getElementById("complianceResult").innerHTML = `
        <div class="card">
            <h3>Compliance Insights</h3>
            ${
                insights.length > 0
                    ? insights.map(i => `
                        <div class="result">
                            <span class="badge ${badgeClass(i.level)}">${safeValue(i.level)}</span>
                            <b>Score: ${safeNumber(i.compliance_score)}/100</b><br>
                            Elementi: ${safeNumber(i.total_items)}<br>
                            Completati: ${safeNumber(i.completed_items)}<br>
                            Pendenti: ${safeNumber(i.pending_items)}<br>
                            Scaduti: ${safeNumber(i.expired_items)}<br>
                            Data: ${safeValue(i.created_at)}<br><br>
                            <b>Messaggio:</b>
                            <p>${safeValue(i.message)}</p>
                            <b>Raccomandazione:</b>
                            <p>${safeValue(i.recommendation)}</p>
                        </div>
                    `).join("")
                    : "<p>Nessun insight compliance disponibile.</p>"
            }
        </div>
    `;
}