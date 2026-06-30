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

    if (!Array.isArray(data)) {
        document.getElementById("reportsResult").innerHTML =
            `<div class="result">${data.error || "Errore timeline"}</div>`;
        return;
    }

    document.getElementById("reportsResult").innerHTML = `
        <div class="card">
            <h3>📈 Oracle Score Timeline</h3>
            ${
                data.length > 0
                    ? data.map((s, i) => `
                        <div class="result">
                            <span class="badge badge-blue">Snapshot #${i + 1}</span>
                            <b>Oracle Score: ${s.oracle_score}/100</b>
                            ${progressBar(s.oracle_score)}
                            Finance: ${s.finance_score}<br>
                            Business Health: ${s.business_health_score}<br>
                            Customer: ${s.customer_score}<br>
                            Compliance: ${s.compliance_score}<br>
                            Cyber: ${s.cyber_score}<br>
                            Data: ${s.created_at}
                        </div>
                    `).join("")
                    : "<p>Nessuno storico Oracle disponibile.</p>"
            }
        </div>
    `;
}

async function loadCyberTimelineReport() {
    const companyId = getCompanyId();
    const data = await apiGet(`/api/cyber-timeline/${companyId}`);

    if (!Array.isArray(data)) {
        document.getElementById("reportsResult").innerHTML =
            `<div class="result">${data.error || "Errore cyber timeline"}</div>`;
        return;
    }

    document.getElementById("reportsResult").innerHTML = `
        <div class="card">
            <h3>🛡 Cyber Timeline</h3>
            ${
                data.length > 0
                    ? data.map((s, i) => `
                        <div class="result">
                            <span class="badge badge-blue">Cyber Snapshot #${i + 1}</span>
                            <b>Cyber Score: ${s.cyber_score}/100</b>
                            ${progressBar(s.cyber_score)}
                            Exposure: ${s.exposure_score}<br>
                            Vulnerability: ${s.vulnerability_score}<br>
                            Threat: ${s.threat_score}<br>
                            Prediction: ${s.prediction_score}<br>
                            Data: ${s.created_at}
                        </div>
                    `).join("")
                    : "<p>Nessuno storico cyber disponibile.</p>"
            }
        </div>
    `;
}

async function loadRevenueAnalyticsReport() {
    const companyId = getCompanyId();
    const data = await apiGet(`/api/revenue-analytics/${companyId}`);

    if (data.error) {
        document.getElementById("reportsResult").innerHTML =
            `<div class="result">${data.error}</div>`;
        return;
    }

    document.getElementById("reportsResult").innerHTML = `
        <div class="card">
            <h3>💶 Revenue Analytics</h3>

            <div class="kpi-grid">
                <div class="kpi">
                    <div class="kpi-title">Entrate totali</div>
                    <div class="kpi-value">€${data.total_revenue}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Operazioni</div>
                    <div class="kpi-value">${data.operations}</div>
                </div>
            </div>

            <div class="result">
                <h3>Trend entrate</h3>
                ${
                    data.trend && data.trend.length > 0
                        ? data.trend.map(x => `
                            <p>
                                <b>${x.label}</b> — €${x.amount}
                                — Totale progressivo: €${x.total}
                                — ${x.payment_method}
                            </p>
                        `).join("")
                        : "Nessun dato revenue."
                }
            </div>
        </div>
    `;
}