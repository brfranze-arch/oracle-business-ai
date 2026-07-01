function safeValue(value, fallback = "N/D") {
    if (value === undefined || value === null || value === "" || Number.isNaN(value)) {
        return fallback;
    }
    return value;
}

function safeNumber(value, fallback = 0) {
    const n = Number(value);
    return Number.isFinite(n) ? n : fallback;
}

function normalizeExecutiveData(data) {
    return {
        company_name: safeValue(data.company_name, "Azienda"),
        oracle_score: safeNumber(data.oracle_score),
        oracle_level: safeValue(data.oracle_level || data.level, "STABILE"),
        total_revenue: safeNumber(data.total_revenue),
        operations: safeNumber(data.operations || data.total_operations || data.count),
        customers: safeNumber(data.customers || data.customers_count),
        top_customer: safeValue(data.top_customer || data.top_customer_name, "N/D"),
        compliance_items: safeNumber(data.compliance_items || data.total_items),
        cyber_score: safeNumber(data.cyber_score),
        attack_probability_30d: safeNumber(data.attack_probability_30d),
        attack_probability_90d: safeNumber(data.attack_probability_90d),
        suggestions: Array.isArray(data.suggestions) ? data.suggestions : [],
        risks: Array.isArray(data.risks) ? data.risks : []
    };
}

async function renderDashboard() {
    setPageTitle("Executive Dashboard");

    setContent(`
        <div class="dashboard-hero">
            <div>
                <h1>Oracle Business AI Enterprise</h1>
                <p>Executive intelligence, cyber risk, finance, customer, compliance e AI assistant in un’unica piattaforma.</p>
            </div>

            <button onclick="loadExecutiveDashboard()">
                Aggiorna Dashboard
            </button>
        </div>

        <div id="dashboardResult">
            <div class="card">
                <h2>🚀 Executive Dashboard</h2>
                <p>Caricamento dati aziendali...</p>
            </div>
        </div>
    `);

    await loadExecutiveDashboard();
}

async function loadExecutiveDashboard() {
    const companyId = getCompanyId();

    const raw = await apiGet(`/api/executive-dashboard/${companyId}`);

    if (raw.error) {
        document.getElementById("dashboardResult").innerHTML =
            `<div class="result">${raw.error}</div>`;
        return;
    }

    const data = normalizeExecutiveData(raw);

    if (typeof buildNotifications === "function" && typeof renderNotificationCenter === "function") {
        renderNotificationCenter(buildNotifications(data));
    }

    document.getElementById("dashboardResult").innerHTML = `
        <div class="kpi-grid enterprise-kpis">

            <div class="kpi enterprise-kpi">
                <div class="kpi-title">🏆 Oracle Score</div>
                <div class="kpi-value counter" data-target="${data.oracle_score}">0</div>
                <span class="badge ${badgeClass(data.oracle_level)}">${data.oracle_level}</span>
                ${progressBar(data.oracle_score)}
            </div>

            <div class="kpi enterprise-kpi">
                <div class="kpi-title">💰 Revenue</div>
                <div class="kpi-value">€${data.total_revenue}</div>
                <span class="badge badge-blue">${data.operations} operazioni</span>
            </div>

            <div class="kpi enterprise-kpi">
                <div class="kpi-title">👥 Customer</div>
                <div class="kpi-value counter" data-target="${data.customers}">0</div>
                <span class="badge badge-blue">Top: ${data.top_customer}</span>
            </div>

            <div class="kpi enterprise-kpi">
                <div class="kpi-title">🛡 Cyber Risk</div>
                <div class="kpi-value counter" data-target="${data.cyber_score}">0</div>
                <span class="badge badge-yellow">30d: ${data.attack_probability_30d}%</span>
                <span class="badge badge-red">90d: ${data.attack_probability_90d}%</span>
                ${progressBar(data.cyber_score)}
            </div>

        </div>

        <div class="grid-2">
            <div class="card">
                <h2>🤖 Oracle AI Suggestions</h2>
                ${
                    data.suggestions.length > 0
                    ? data.suggestions.map(x => `
                        <div class="action-item">
                            <span>🎯</span>
                            <p>${x}</p>
                        </div>
                    `).join("")
                    : `<p>Nessuna azione urgente.</p>`
                }
            </div>

            <div class="card">
                <h2>⚠️ Risk Center</h2>
                ${
                    data.risks.length > 0
                    ? data.risks.map(x => `
                        <div class="risk-item">
                            <span>⚠️</span>
                            <p>${x}</p>
                        </div>
                    `).join("")
                    : `<p>Nessun rischio importante rilevato.</p>`
                }
            </div>
        </div>

        <div class="grid-2">
            <div class="card">
                <h2>🧠 Daily Brief</h2>
                <button onclick="loadDailyBrief()">Genera Daily Brief AI</button>
                <div id="dailyBriefInline"></div>
            </div>

            <div class="card">
                <h2>📊 Quick Reports</h2>
                <button onclick="showPage('reports')">Apri Reports</button>
                <button onclick="showPage('cyber')">Apri Cyber Oracle AI</button>
                <button onclick="showPage('assistant')">Apri Assistant</button>
            </div>
        </div>
    `;

    document.getElementById("pageTitle").innerText = "Executive Dashboard ✓ aggiornato";

    animateCounters();
}

async function loadDailyBrief() {
    const companyId = getCompanyId();

    const data = await apiGet(`/api/daily-brief/${companyId}`);

    if (data.error) {
        document.getElementById("dailyBriefInline").innerHTML =
            `<div class="result">${data.error}</div>`;
        return;
    }

    document.getElementById("dailyBriefInline").innerHTML = `
        <div class="result">
            <span class="badge ${badgeClass(data.level)}">${safeValue(data.level, "STABILE")}</span>
            <h3>Oracle Score ${safeNumber(data.oracle_score)}/100</h3>
            ${progressBar(safeNumber(data.oracle_score))}

            <h4>📌 Sintesi</h4>
            <ul>${(data.brief || []).map(x => `<li>${x}</li>`).join("")}</ul>

            <h4>🎯 Priorità</h4>
            <ul>${(data.priorities || []).map(x => `<li>${x}</li>`).join("")}</ul>
        </div>
    `;
}

function animateCounters() {
    document.querySelectorAll(".counter").forEach(el => {
        const target = Number(el.dataset.target || 0);
        let current = 0;
        const steps = 30;
        const increment = target / steps;

        const timer = setInterval(() => {
            current += increment;

            if (current >= target) {
                current = target;
                clearInterval(timer);
            }

            el.innerText = Math.round(current * 100) / 100;
        }, 20);
    });
}