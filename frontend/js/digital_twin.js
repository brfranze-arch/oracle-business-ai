async function runDigitalTwin() {
    const companyId = getCompanyId();

    document.getElementById("reportsResult").innerHTML = `
        <div class="result">Digital Twin Engine sta correlando Finanza, Clienti, Compliance, Cyber, OSINT, Predictive e Agents...</div>
    `;

    const data = await apiPost(`/api/digital-twin/analyze/${companyId}`);

    if (data.error) {
        showError("reportsResult", data.error);
        return;
    }

    renderDigitalTwinSnapshot(data);
}

async function loadDigitalTwinHistory() {
    const companyId = getCompanyId();
    const data = await apiGet(`/api/digital-twin/history/${companyId}`);

    if (data.error) {
        showError("reportsResult", data.error);
        return;
    }

    const snapshots = safeArray(data);

    document.getElementById("reportsResult").innerHTML = `
        <div class="card">
            <h3>🧬 Storico Digital Twin</h3>
            ${snapshots.length > 0
                ? snapshots.map(s => digitalTwinSnapshotHtml(s)).join("")
                : "<p>Nessuno snapshot Digital Twin presente.</p>"}
        </div>
    `;
}

function renderDigitalTwinSnapshot(data) {
    document.getElementById("reportsResult").innerHTML = `
        <div class="card">
            <h3>🧬 Digital Twin aziendale</h3>
            ${digitalTwinSnapshotHtml(data)}
        </div>
    `;
}

function digitalTwinSnapshotHtml(s) {
    const score = safeNumber(s.twin_score);
    const level = safeValue(s.level, "STABILE");

    return `
        <div class="result">
            <span class="badge ${badgeClass(level)}">${level}</span>
            <div class="kpi-value">${score}/100</div>
            ${progressBar(score)}

            <div class="kpi-grid">
                ${digitalTwinKpi("Finanza", s.finance_index)}
                ${digitalTwinKpi("Clienti", s.customer_index)}
                ${digitalTwinKpi("Compliance", s.compliance_index)}
                ${digitalTwinKpi("Cyber", s.cyber_index)}
                ${digitalTwinKpi("OSINT", s.osint_index)}
                ${digitalTwinKpi("Predictive", s.predictive_index)}
                ${digitalTwinKpi("Agents", s.agents_index)}
            </div>

            <h4>Stato corrente</h4>
            <p>${safeValue(s.current_state)}</p>

            <h4>Previsione</h4>
            <p>${safeValue(s.forecast_state)}</p>

            <h4>Scenario</h4>
            <p>${safeValue(s.scenario_summary)}</p>

            <h4>Raccomandazione</h4>
            <p>${safeValue(s.recommendation)}</p>

            <small>${safeValue(s.created_at)}</small>
        </div>
    `;
}

function digitalTwinKpi(label, value) {
    const score = safeNumber(value);
    return `
        <div class="kpi">
            <div class="kpi-title">${label}</div>
            <div class="kpi-value">${score}</div>
            ${progressBar(score)}
        </div>
    `;
}
