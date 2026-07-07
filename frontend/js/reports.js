function renderReports() {
    setPageTitle("Reports & Timeline");

    setContent(`
        <div class="card">
            <h2>📊 Reports & Timeline AI</h2>
            <p>Storico Oracle Score, Cyber Score e andamento aziendale.</p>

            <button onclick="loadOracleTimelineReport()">Oracle Timeline</button>
            <button onclick="loadCyberTimelineReport()">Cyber Timeline</button>
            <button onclick="loadRevenueAnalyticsReport()">Revenue Analytics</button>
            <button onclick="runPredictiveAI()">Predictive AI</button>
            <button onclick="loadPredictiveHistory()">Storico Predictive</button>
            <button onclick="runAutonomousAgents()">Autonomous Agents</button>
            <button onclick="loadAgentsHistory()">Storico Agents</button>

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

async function runPredictiveAI() {
    const companyId = getCompanyId();

    document.getElementById("reportsResult").innerHTML = `
        <div class="result">
            Predictive AI sta analizzando Finance, Customer, Compliance e Cyber...
        </div>
    `;

    const data = await apiPost(`/api/predictive/analyze/${companyId}`);

    if (data.error) {
        showError("reportsResult", data.error);
        return;
    }

    const score = safeNumber(data.prediction_score);
    const level = safeValue(data.level, "STABILE");

    document.getElementById("reportsResult").innerHTML = `
        <div class="card">
            <h3>🔮 Predictive AI</h3>

            <span class="badge ${badgeClass(level)}">${level}</span>

            <div class="kpi-value">${score}/100</div>
            ${progressBar(score)}

            <div class="kpi-grid">
                <div class="kpi">
                    <div class="kpi-title">Finance Risk</div>
                    <div class="kpi-value">${safeNumber(data.finance_risk)}%</div>
                    ${progressBar(safeNumber(data.finance_risk))}
                </div>

                <div class="kpi">
                    <div class="kpi-title">Customer Risk</div>
                    <div class="kpi-value">${safeNumber(data.customer_risk)}%</div>
                    ${progressBar(safeNumber(data.customer_risk))}
                </div>

                <div class="kpi">
                    <div class="kpi-title">Compliance Risk</div>
                    <div class="kpi-value">${safeNumber(data.compliance_risk)}%</div>
                    ${progressBar(safeNumber(data.compliance_risk))}
                </div>

                <div class="kpi">
                    <div class="kpi-title">Cyber Risk</div>
                    <div class="kpi-value">${safeNumber(data.cyber_risk)}%</div>
                    ${progressBar(safeNumber(data.cyber_risk))}
                </div>
            </div>

            <div class="result">
                <h3>Sintesi predittiva</h3>
                <p>${safeValue(data.summary)}</p>
            </div>

            <div class="result">
                <h3>Raccomandazione</h3>
                <p>${safeValue(data.recommendation)}</p>
            </div>
        </div>
    `;
}

async function loadPredictiveHistory() {
    const companyId = getCompanyId();

    const data = await apiGet(`/api/predictive/history/${companyId}`);

    if (data.error) {
        showError("reportsResult", data.error);
        return;
    }

    const insights = safeArray(data);

    document.getElementById("reportsResult").innerHTML = `
        <div class="card">
            <h3>🔮 Storico Predictive AI</h3>

            ${
                insights.length > 0
                    ? insights.map(i => `
                        <div class="result">
                            <span class="badge ${badgeClass(i.level)}">${safeValue(i.level)}</span>
                            <b>Prediction Score: ${safeNumber(i.prediction_score)}/100</b>
                            ${progressBar(safeNumber(i.prediction_score))}

                            Finance Risk: ${safeNumber(i.finance_risk)}%<br>
                            Customer Risk: ${safeNumber(i.customer_risk)}%<br>
                            Compliance Risk: ${safeNumber(i.compliance_risk)}%<br>
                            Cyber Risk: ${safeNumber(i.cyber_risk)}%<br>
                            Data: ${safeValue(i.created_at)}<br><br>

                            <b>Sintesi:</b>
                            <p>${safeValue(i.summary)}</p>

                            <b>Raccomandazione:</b>
                            <p>${safeValue(i.recommendation)}</p>
                        </div>
                    `).join("")
                    : "<p>Nessuna analisi predittiva ancora presente.</p>"
            }
        </div>
    `;
}

async function runAutonomousAgents() {

    const companyId = getCompanyId();

    document.getElementById("reportsResult").innerHTML = `
        <div class="result">
            Gli Autonomous Agents stanno analizzando l'azienda...
        </div>
    `;

    const data = await apiPost(`/api/agents/run/${companyId}`);

    if (data.error) {
        showError("reportsResult", data.error);
        return;
    }

    renderAgents(data);
}

async function loadAgentsHistory() {

    const companyId = getCompanyId();

    const data = await apiGet(`/api/agents/history/${companyId}`);

    if (data.error) {
        showError("reportsResult", data.error);
        return;
    }

    renderAgents(data);
}

function renderAgents(list) {

    const agents = safeArray(list);

    document.getElementById("reportsResult").innerHTML = `
        <div class="card">

            <h2>🤖 Autonomous Agents</h2>

            ${
                agents.map(agent => `

                    <div class="result">

                        <span class="badge ${priorityBadge(agent.priority)}">

                            ${safeValue(agent.priority)}

                        </span>

                        <h3>${safeValue(agent.agent_name)}</h3>

                        <b>Status:</b>

                        ${safeValue(agent.status)}

                        <br><br>

                        <b>Sintesi</b>

                        <p>${safeValue(agent.summary)}</p>

                        <b>Azioni consigliate</b>

                        <p>${safeValue(agent.actions)}</p>

                        <small>

                            ${safeValue(agent.created_at)}

                        </small>

                    </div>

                `).join("")
            }

        </div>
    `;
}

function priorityBadge(priority){

    switch((priority || "").toLowerCase()){

        case "high":
            return "badge-red";

        case "medium":
            return "badge-yellow";

        case "low":
            return "badge-green";

        default:
            return "badge-blue";
    }

}

