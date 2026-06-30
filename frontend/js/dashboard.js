async function renderDashboard() {
    setPageTitle("Executive Dashboard");

    const companyId = getCompanyId();

    setContent(`
        <div class="card">
            <h2>🚀 Oracle Executive Dashboard</h2>
            <p>Vista centrale dell'azienda con score, rischi e priorità AI.</p>
            <button onclick="loadExecutiveDashboard()">Carica Dashboard</button>
            <button onclick="loadDailyBrief()">Genera Daily Brief</button>
            <div id="dashboardResult"></div>
        </div>
    `);
}

async function loadExecutiveDashboard() {
    const companyId = getCompanyId();

    const data = await apiGet(`/api/executive-dashboard/${companyId}`);

    if (data.error) {
        document.getElementById("dashboardResult").innerHTML =
            `<div class="result">${data.error}</div>`;
        return;
    }

    document.getElementById("dashboardResult").innerHTML = `
        <div class="card">
            <h2>🏢 ${data.company_name}</h2>

            <span class="badge ${badgeClass(data.oracle_level)}">
                ${data.oracle_level}
            </span>

            <div class="kpi-value">
                Oracle Score ${data.oracle_score}
            </div>

            ${progressBar(data.oracle_score)}

            <div class="kpi-grid">
                <div class="kpi">
                    <div class="kpi-title">💰 Entrate</div>
                    <div class="kpi-value">€${data.total_revenue}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">📊 Operazioni</div>
                    <div class="kpi-value">${data.operations}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">👥 Clienti</div>
                    <div class="kpi-value">${data.customers}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">🛡 Cyber Score</div>
                    <div class="kpi-value">${data.cyber_score}</div>
                </div>
            </div>

            <div class="result">
                <h3>🎯 Probabilità attacco</h3>
                <span class="badge badge-yellow">30 giorni: ${data.attack_probability_30d}%</span>
                <span class="badge badge-red">90 giorni: ${data.attack_probability_90d}%</span>
            </div>

            <div class="result">
                <h3>⚠️ Rischi</h3>
                <ul>${(data.risks || []).map(x => `<li>${x}</li>`).join("") || "<li>Nessun rischio rilevato.</li>"}</ul>
            </div>

            <div class="result">
                <h3>🤖 Azioni consigliate</h3>
                <ul>${(data.suggestions || []).map(x => `<li>${x}</li>`).join("") || "<li>Nessuna azione urgente.</li>"}</ul>
            </div>
        </div>
    `;
}

async function loadDailyBrief() {
    const companyId = getCompanyId();

    const data = await apiGet(`/api/daily-brief/${companyId}`);

    if (data.error) {
        document.getElementById("dashboardResult").innerHTML =
            `<div class="result">${data.error}</div>`;
        return;
    }

    document.getElementById("dashboardResult").innerHTML = `
        <div class="card">
            <h2>🧠 Oracle Daily Brief — ${data.company_name}</h2>

            <span class="badge ${badgeClass(data.level)}">
                ${data.level}
            </span>

            <div class="kpi-value">
                Oracle Score ${data.oracle_score}/100
            </div>

            ${progressBar(data.oracle_score)}

            <div class="result">
                <h3>📌 Sintesi</h3>
                <ul>${data.brief.map(x => `<li>${x}</li>`).join("")}</ul>
            </div>

            <div class="result">
                <h3>🎯 Priorità di oggi</h3>
                <ul>${data.priorities.map(x => `<li>${x}</li>`).join("")}</ul>
            </div>
        </div>
    `;
}