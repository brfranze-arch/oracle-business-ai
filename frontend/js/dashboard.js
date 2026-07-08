function safeValue(value, fallback = "N/D") {
    if (value === undefined || value === null || value === "" || Number.isNaN(value)) return fallback;
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
        <div class="enterprise-shell">
            <div class="enterprise-hero-v2">
                <div>
                    <span class="eyebrow">Oracle Business AI / Enterprise Command Center</span>
                    <h1>Executive Dashboard 2.0</h1>
                    <p>Finance, Customer, Compliance, Cyber, OSINT, Predictive AI, Agents e OpenAI Advisor in una singola vista decisionale.</p>
                    <div class="hero-actions">
                        <button onclick="loadExecutiveDashboard()">Aggiorna intelligence</button>
                        <button onclick="showPage('reports')">Apri Reports</button>
                        <button onclick="showPage('assistant')">Chiedi all'AI</button>
                    </div>
                </div>
                <div class="hero-orb">
                    <div>AI</div>
                    <span>Live intelligence</span>
                </div>
            </div>

            <div id="dashboardResult">
                <div class="card"><h2>Caricamento Executive Dashboard...</h2></div>
            </div>
        </div>
    `);
    await loadExecutiveDashboard();
}

async function loadExecutiveDashboard() {
    const companyId = getCompanyId();
    const raw = await apiGet(`/api/executive-dashboard/${companyId}`);
    if (raw.error) {
        document.getElementById("dashboardResult").innerHTML = `<div class="result">${raw.error}</div>`;
        return;
    }

    const data = normalizeExecutiveData(raw);
    const healthIndex = Math.round((data.oracle_score + data.cyber_score + Math.min(100, data.operations * 8) + Math.min(100, data.customers * 12)) / 4);
    const aiConfidence = Math.max(55, Math.min(98, Math.round((data.oracle_score + 100 - data.attack_probability_30d) / 2)));
    const decisionQuality = Math.max(40, Math.min(100, Math.round((data.oracle_score * 0.5) + (data.operations > 0 ? 25 : 5) + (data.customers > 0 ? 20 : 5))));

    if (typeof buildNotifications === "function" && typeof renderNotificationCenter === "function") {
        renderNotificationCenter(buildNotifications(data));
    }

    document.getElementById("dashboardResult").innerHTML = `
        <div class="executive-summary-card">
            <div>
                <span class="eyebrow">Executive AI Summary</span>
                <h2>${data.company_name}</h2>
                <p>${buildExecutiveSummary(data)}</p>
            </div>
            <div class="summary-score">
                <span>Oracle Score</span>
                <strong class="counter" data-target="${data.oracle_score}">0</strong>
                <em>${data.oracle_level}</em>
            </div>
        </div>

        ${renderLiveStatus(data)}

        <div class="kpi-grid enterprise-kpis-v2">
            ${renderKpiCard("🏆", "Oracle Score", data.oracle_score, data.oracle_level, "+ intelligence", true)}
            ${renderMoneyKpi("💰", "Revenue", data.total_revenue, `${data.operations} operazioni`)}
            ${renderKpiCard("👥", "Customer", data.customers, `Top: ${data.top_customer}`, "client intelligence", false)}
            ${renderKpiCard("🛡", "Cyber Score", data.cyber_score, `30d: ${data.attack_probability_30d}%`, `90d: ${data.attack_probability_90d}%`, true)}
        </div>

        <div class="grid-2">
            <div class="card enterprise-widget">
                <h2>🧠 Decision Intelligence</h2>
                <div class="mini-metrics">
                    ${renderMiniMetric("AI Confidence", aiConfidence)}
                    ${renderMiniMetric("Decision Quality", decisionQuality)}
                    ${renderMiniMetric("Enterprise Index", healthIndex)}
                </div>
            </div>
            <div class="card enterprise-widget">
                <h2>📡 Oracle Live Status</h2>
                <div class="status-grid">
                    ${statusPill("Finance", data.operations > 0)}
                    ${statusPill("Customer", data.customers > 0)}
                    ${statusPill("Compliance", data.compliance_items > 0)}
                    ${statusPill("Cyber", data.cyber_score >= 50)}
                    ${statusPill("OpenAI", true)}
                    ${statusPill("Billing", true)}
                    ${statusPill("Predictive", data.oracle_score > 0)}
                    ${statusPill("Agents", true)}
                </div>
            </div>
        </div>

        <div class="grid-2">
            <div class="card enterprise-widget">
                <h2>🎯 AI Suggestions</h2>
                ${renderActionList(data.suggestions, "Nessuna azione urgente.")}
            </div>
            <div class="card enterprise-widget">
                <h2>⚠️ Risk Center</h2>
                ${renderRiskList(data.risks, "Nessun rischio importante rilevato.")}
            </div>
        </div>

        <div class="grid-2">
            <div class="card enterprise-widget">
                <h2>🕒 Live Timeline</h2>
                ${renderLiveTimeline(data)}
            </div>
            <div class="card enterprise-widget">
                <h2>🤖 Executive Controls</h2>
                <button onclick="loadDailyBrief()">Genera Daily Brief AI</button>
                <button onclick="showPage('reports')">Predictive / Agents</button>
                <button onclick="showPage('cyber')">Cyber + OSINT</button>
                <button onclick="showPage('billing')">Billing SaaS</button>
                <div id="dailyBriefInline"></div>
            </div>
        </div>
    `;

    document.getElementById("pageTitle").innerText = "Executive Dashboard ✓ live";
    animateCounters();
}

function buildExecutiveSummary(data) {
    const points = [];
    points.push(`Oracle Score ${data.oracle_score}/100, livello ${data.oracle_level}.`);
    points.push(`Revenue registrata: €${data.total_revenue} su ${data.operations} operazioni.`);
    points.push(`Clienti: ${data.customers}; Cyber Score: ${data.cyber_score}/100.`);
    if (data.risks.length > 0) points.push(`${data.risks.length} rischio/i richiedono attenzione.`);
    else points.push("Nessuna criticità primaria rilevata nel perimetro corrente.");
    return points.join(" ");
}

function renderKpiCard(icon, title, value, badge, footer, withBar) {
    return `
        <div class="kpi enterprise-kpi-v2">
            <div class="kpi-icon">${icon}</div>
            <div class="kpi-title">${title}</div>
            <div class="kpi-value counter" data-target="${safeNumber(value)}">0</div>
            <span class="badge ${badgeClass(badge)}">${safeValue(badge)}</span>
            ${withBar ? progressBar(safeNumber(value)) : ""}
            <small>${safeValue(footer)}</small>
        </div>
    `;
}

function renderMoneyKpi(icon, title, amount, footer) {
    return `
        <div class="kpi enterprise-kpi-v2">
            <div class="kpi-icon">${icon}</div>
            <div class="kpi-title">${title}</div>
            <div class="kpi-value">€${safeNumber(amount)}</div>
            <span class="badge badge-blue">${safeValue(footer)}</span>
            <small>Cash flow intelligence</small>
        </div>
    `;
}

function renderMiniMetric(label, value) {
    return `
        <div class="mini-metric">
            <span>${label}</span>
            <strong>${safeNumber(value)}%</strong>
            ${progressBar(safeNumber(value))}
        </div>
    `;
}

function statusPill(label, ok) {
    return `<span class="live-pill ${ok ? "ok" : "warn"}">${ok ? "🟢" : "🟡"} ${label}</span>`;
}

function renderLiveStatus(data) {
    return `
        <div class="live-strip">
            ${statusPill("Finance", data.operations > 0)}
            ${statusPill("Customer", data.customers > 0)}
            ${statusPill("Compliance", data.compliance_items > 0)}
            ${statusPill("Cyber", data.cyber_score >= 50)}
            ${statusPill("OpenAI", true)}
            ${statusPill("Billing", true)}
            ${statusPill("OSINT", data.cyber_score > 0)}
            ${statusPill("Agents", true)}
        </div>
    `;
}

function renderActionList(items, emptyText) {
    if (!items || items.length === 0) return `<p>${emptyText}</p>`;
    return items.map(x => `<div class="action-item"><span>🎯</span><p>${x}</p></div>`).join("");
}

function renderRiskList(items, emptyText) {
    if (!items || items.length === 0) return `<p>${emptyText}</p>`;
    return items.map(x => `<div class="risk-item"><span>⚠️</span><p>${x}</p></div>`).join("");
}

function renderLiveTimeline(data) {
    const events = [
        ["Executive", `Dashboard aggiornata per ${data.company_name}`],
        ["Finance", `Revenue €${data.total_revenue}, operazioni ${data.operations}`],
        ["Customer", `Clienti registrati: ${data.customers}`],
        ["Cyber", `Cyber Score ${data.cyber_score}/100, rischio 30d ${data.attack_probability_30d}%`],
        ["Oracle AI", data.risks.length ? `${data.risks.length} rischi rilevati` : "Nessun rischio critico rilevato"]
    ];

    return `<div class="timeline-v2">${events.map((e, i) => `
        <div class="timeline-row">
            <span>${new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}</span>
            <b>${e[0]}</b>
            <p>${e[1]}</p>
        </div>
    `).join("")}</div>`;
}

async function loadDailyBrief() {
    const companyId = getCompanyId();
    const data = await apiGet(`/api/daily-brief/${companyId}`);
    if (data.error) {
        document.getElementById("dailyBriefInline").innerHTML = `<div class="result">${data.error}</div>`;
        return;
    }
    document.getElementById("dailyBriefInline").innerHTML = `
        <div class="result daily-brief-box">
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
            if (current >= target) { current = target; clearInterval(timer); }
            el.innerText = Math.round(current * 100) / 100;
        }, 18);
    });
}
