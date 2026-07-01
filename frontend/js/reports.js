function renderReports() {
    setPageTitle("Reports & Timeline");

    setContent(`
        <div class="card">
            <h2>📊 Reports & Timeline AI</h2>
            <p>Storico Oracle Score, Cyber Score e andamento aziendale.</p>

            <button onclick="loadOracleTimelineReport()">Oracle Timeline</button>
            <button onclick="loadCyberTimelineReport()">Cyber Timeline</button>
            <button onclick="loadRevenueAnalyticsReport()">Revenue Analytics</button>

            <div id="reportsResult"></div>
        </div>
    `);
}

async function loadOracleTimelineReport() {
    const companyId = getCompanyId();
    const data = await apiGet(`/api/oracle-timeline/${companyId}`);

    if (data.error) {
        showError("reportsResult", data.error);
        return;
    }

    const timeline = safeArray(data);

    document.getElementById("reportsResult").innerHTML = `
        <div class="card">
            <h3>📈 Oracle Score Timeline</h3>
            ${
                timeline.length > 0
                    ? timeline.map((s, i) => `
                        <div class="result">
                            <span class="badge badge-blue">Snapshot #${i + 1}</span>
                            <b>Oracle Score: ${safeNumber(s.oracle_score)}/100</b>
                            ${progressBar(safeNumber(s.oracle_score))}
                            Finance: ${safeNumber(s.finance_score)}<br>
                            Business Health: ${safeNumber(s.business_health_score)}<br>
                            Customer: ${safeNumber(s.customer_score)}<br>
                            Compliance: ${safeNumber(s.compliance_score)}<br>
                            Cyber: ${safeNumber(s.cyber_score)}<br>
                            Data: ${safeValue(s.created_at)}
                        </div>
                    `).join("")
                    : "<p>Nessuno storico Oracle disponibile. Calcola Oracle Score almeno una volta.</p>"
            }
        </div>
    `;
}

async function loadCyberTimelineReport() {
    const companyId = getCompanyId();
    const data = await apiGet(`/api/cyber-timeline/${companyId}`);

    if (data.error) {
        showError("reportsResult", data.error);
        return;
    }

    const timeline = safeArray(data);

    document.getElementById("reportsResult").innerHTML = `
        <div class="card">
            <h3>🛡 Cyber Timeline</h3>
            ${
                timeline.length > 0
                    ? timeline.map((s, i) => `
                        <div class="result">
                            <span class="badge badge-blue">Cyber Snapshot #${i + 1}</span>
                            <b>Cyber Score: ${safeNumber(s.cyber_score)}/100</b>
                            ${progressBar(safeNumber(s.cyber_score))}
                            Exposure: ${safeNumber(s.exposure_score)}<br>
                            Vulnerability: ${safeNumber(s.vulnerability_score)}<br>
                            Threat: ${safeNumber(s.threat_score)}<br>
                            Prediction: ${safeNumber(s.prediction_score)}<br>
                            Data: ${safeValue(s.created_at)}
                        </div>
                    `).join("")
                    : "<p>Nessuna cyber timeline disponibile. Esegui Cyber Oracle AI almeno una volta.</p>"
            }
        </div>
    `;
}

async function loadRevenueAnalyticsReport() {
    const companyId = getCompanyId();
    const data = await apiGet(`/api/revenue-analytics/${companyId}`);

    if (data.error) {
        showError("reportsResult", data.error);
        return;
    }

    const trend = safeArray(data.trend);

    document.getElementById("reportsResult").innerHTML = `
        <div class="card">
            <h3>💶 Revenue Analytics</h3>

            <div class="kpi-grid">
                <div class="kpi">
                    <div class="kpi-title">Entrate totali</div>
                    <div class="kpi-value">€${safeNumber(data.total_revenue)}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Operazioni</div>
                    <div class="kpi-value">${safeNumber(data.operations)}</div>
                </div>
            </div>

            <div class="result">
                <h3>Trend entrate</h3>
                ${
                    trend.length > 0
                        ? trend.map(x => `
                            <p>
                                <b>${safeValue(x.label)}</b> —
                                €${safeNumber(x.amount)} —
                                Totale progressivo: €${safeNumber(x.total)} —
                                ${safeValue(x.payment_method)}
                            </p>
                        `).join("")
                        : "Nessun dato revenue disponibile."
                }
            </div>
        </div>
    `;
}