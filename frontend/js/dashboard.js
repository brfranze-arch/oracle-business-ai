function localSafeValue(value, fallback = "N/D") {
    if (value === undefined || value === null || value === "" || Number.isNaN(value)) {
        return fallback;
    }
    return value;
}

function localSafeNumber(value, fallback = 0) {
    const n = Number(value);
    return Number.isFinite(n) ? n : fallback;
}

function localSafeArray(value) {
    return Array.isArray(value) ? value : [];
}

function formatEuro(value) {
    return new Intl.NumberFormat("it-IT", {
        style: "currency",
        currency: "EUR",
        maximumFractionDigits: 0
    }).format(localSafeNumber(value));
}

function normalizeExecutiveData(data) {
    return {
        company_name: localSafeValue(data.company_name, "Azienda"),
        oracle_score: localSafeNumber(data.oracle_score),
        oracle_level: localSafeValue(data.oracle_level || data.level, "STABILE"),
        total_revenue: localSafeNumber(data.total_revenue),
        operations: localSafeNumber(data.operations || data.total_operations || data.count),
        customers: localSafeNumber(data.customers || data.customers_count),
        top_customer: localSafeValue(data.top_customer || data.top_customer_name, "N/D"),
        compliance_items: localSafeNumber(data.compliance_items || data.total_items),
        cyber_score: localSafeNumber(data.cyber_score),
        attack_probability_30d: localSafeNumber(data.attack_probability_30d),
        attack_probability_90d: localSafeNumber(data.attack_probability_90d),
        suggestions: localSafeArray(data.suggestions),
        risks: localSafeArray(data.risks)
    };
}

function dashboardHealthLabel(score) {
    const s = localSafeNumber(score);
    if (s >= 75) return "Enterprise Ready";
    if (s >= 60) return "Operativo";
    if (s >= 40) return "Da consolidare";
    return "Critico";
}

function dashboardTrendLabel(score) {
    const s = localSafeNumber(score);
    if (s >= 75) return "+ alta affidabilità";
    if (s >= 60) return "+ stabile";
    if (s >= 40) return "attenzione";
    return "intervento prioritario";
}

async function renderDashboard() {
    setPageTitle("Executive Dashboard 2.0");

    setContent(`
        <div class="dashboard-hero enterprise-hero-v2">
            <div>
                <div class="eyebrow">Oracle Business AI · Release Candidate</div>
                <h1>Executive Command Center</h1>
                <p>Digital intelligence per Finance, Customer, Compliance, Cyber, OSINT, Predictive AI, Billing e Autonomous Agents.</p>
            </div>

            <div class="hero-actions">
                <button onclick="loadExecutiveDashboard()">Aggiorna Command Center</button>
                <button onclick="loadDailyBrief()">Genera Daily Brief</button>
            </div>
        </div>

        <div id="dashboardResult">
            <div class="card enterprise-loading-card">
                <h2>🚀 Caricamento Executive Intelligence</h2>
                <p>Oracle Business AI sta correlando i dati aziendali.</p>
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

    if (typeof buildNotifications === "function" && typeof renderNotificationCenter === "function") {
        renderNotificationCenter(buildNotifications(data));
    }

    const executiveMessage = buildExecutiveSummary(data);
    const liveStatus = buildLiveStatus(data);
    const timeline = buildLiveTimeline(data);

    document.getElementById("dashboardResult").innerHTML = `
        <div class="executive-summary-panel">
            <div>
                <div class="eyebrow">Executive AI Summary</div>
                <h2>${data.company_name}</h2>
                <p>${executiveMessage}</p>
            </div>
            <div class="summary-score-card">
                <span class="badge ${badgeClass(data.oracle_level)}">${data.oracle_level}</span>
                <div class="summary-score counter" data-target="${data.oracle_score}">0</div>
                <small>Oracle Score</small>
            </div>
        </div>

        <div class="live-status-strip">
            ${liveStatus.map(item => `
                <div class="status-pill ${item.status}">
                    <span>${item.icon}</span>
                    <b>${item.label}</b>
                    <small>${item.text}</small>
                </div>
            `).join("")}
        </div>

        <div class="kpi-grid enterprise-kpis">
            <div class="kpi enterprise-kpi premium-kpi">
                <div class="kpi-title">🏆 Oracle Score</div>
                <div class="kpi-value counter" data-target="${data.oracle_score}">0</div>
                <span class="badge ${badgeClass(data.oracle_level)}">${data.oracle_level}</span>
                ${progressBar(data.oracle_score)}
                <small>${dashboardTrendLabel(data.oracle_score)}</small>
            </div>

            <div class="kpi enterprise-kpi premium-kpi">
                <div class="kpi-title">💰 Revenue</div>
                <div class="kpi-value">${formatEuro(data.total_revenue)}</div>
                <span class="badge badge-blue">${data.operations} operazioni</span>
                <small>cash intelligence</small>
            </div>

            <div class="kpi enterprise-kpi premium-kpi">
                <div class="kpi-title">👥 Customer</div>
                <div class="kpi-value counter" data-target="${data.customers}">0</div>
                <span class="badge badge-blue">Top: ${data.top_customer}</span>
                <small>customer concentration</small>
            </div>

            <div class="kpi enterprise-kpi premium-kpi">
                <div class="kpi-title">🛡 Cyber Risk</div>
                <div class="kpi-value counter" data-target="${data.cyber_score}">0</div>
                <span class="badge badge-yellow">30d: ${data.attack_probability_30d}%</span>
                <span class="badge badge-red">90d: ${data.attack_probability_90d}%</span>
                ${progressBar(data.cyber_score)}
            </div>
        </div>

        <div class="grid-2">
            <div class="card enterprise-widget-card">
                <h2>🧠 Enterprise Widgets</h2>
                <div class="widget-grid-mini">
                    <div><b>AI Confidence</b><span>${Math.min(99, Math.round(data.oracle_score + 12))}%</span></div>
                    <div><b>Decision Quality</b><span>${dashboardHealthLabel(data.oracle_score)}</span></div>
                    <div><b>Digital Twin</b><span>${Math.round((data.oracle_score + data.cyber_score) / 2)}/100</span></div>
                    <div><b>Enterprise Index</b><span>${data.operations + data.customers + data.compliance_items}</span></div>
                </div>
            </div>

            <div class="card enterprise-widget-card">
                <h2>📡 Live Timeline</h2>
                <div class="timeline-list">
                    ${timeline.map(t => `
                        <div class="timeline-row">
                            <span>${t.time}</span>
                            <b>${t.title}</b>
                            <p>${t.text}</p>
                        </div>
                    `).join("")}
                </div>
            </div>
        </div>

        <div class="grid-2">
            <div class="card">
                <h2>🤖 Oracle AI Suggestions</h2>
                ${data.suggestions.length > 0
                    ? data.suggestions.map(x => `<div class="action-item"><span>🎯</span><p>${x}</p></div>`).join("")
                    : `<p>Nessuna azione urgente.</p>`
                }
            </div>

            <div class="card">
                <h2>⚠️ Risk Center</h2>
                ${data.risks.length > 0
                    ? data.risks.map(x => `<div class="risk-item"><span>⚠️</span><p>${x}</p></div>`).join("")
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
                <h2>📊 Quick Actions</h2>
                <button onclick="showPage('reports')">Reports / Predictive / Agents</button>
                <button onclick="showPage('cyber')">Cyber / OSINT</button>
                <button onclick="showPage('assistant')">OpenAI Advisor</button>
            </div>
        </div>
    `;

    document.getElementById("pageTitle").innerText = "Executive Dashboard 2.0 ✓ aggiornato";
    animateCounters();
}

function buildExecutiveSummary(data) {
    const score = localSafeNumber(data.oracle_score);
    if (score >= 75) {
        return "La situazione aziendale è solida. Oracle rileva un buon equilibrio tra revenue, clienti, compliance e rischio cyber.";
    }
    if (score >= 55) {
        return "La situazione è stabile, ma Oracle consiglia di monitorare i moduli con punteggio più basso e aggiornare i dati periodicamente.";
    }
    return "Oracle rileva aree da consolidare. Priorità: aumentare qualità dei dati, ridurre rischi operativi e completare le analisi AI.";
}

function buildLiveStatus(data) {
    return [
        { label: "Finance", icon: "💰", status: data.total_revenue > 0 ? "ok" : "warn", text: data.total_revenue > 0 ? "attivo" : "dati bassi" },
        { label: "Customer", icon: "👥", status: data.customers > 0 ? "ok" : "warn", text: `${data.customers} clienti` },
        { label: "Compliance", icon: "📄", status: data.compliance_items > 0 ? "ok" : "warn", text: `${data.compliance_items} elementi` },
        { label: "Cyber", icon: "🛡", status: data.attack_probability_30d > 25 ? "danger" : "ok", text: `${data.attack_probability_30d}% 30d` },
        { label: "OpenAI", icon: "🧠", status: "ok", text: "advisor ready" },
        { label: "Billing", icon: "💳", status: "ok", text: "SaaS active" }
    ];
}

function buildLiveTimeline(data) {
    const now = new Date();
    const hhmm = now.toLocaleTimeString("it-IT", { hour: "2-digit", minute: "2-digit" });
    return [
        { time: hhmm, title: "Oracle Score", text: `Score aggiornato a ${data.oracle_score}/100.` },
        { time: hhmm, title: "Finance AI", text: `${data.operations} operazioni analizzate.` },
        { time: hhmm, title: "Customer", text: `${data.customers} clienti nel workspace.` },
        { time: hhmm, title: "Cyber Risk", text: `Probabilità 30 giorni: ${data.attack_probability_30d}%.` }
    ];
}

async function loadDailyBrief() {
    const companyId = getCompanyId();
    const data = await apiGet(`/api/daily-brief/${companyId}`);

    if (data.error) {
        const target = document.getElementById("dailyBriefInline") || document.getElementById("dashboardResult");
        target.innerHTML = `<div class="result">${data.error}</div>`;
        return;
    }

    const target = document.getElementById("dailyBriefInline") || document.getElementById("dashboardResult");
    target.innerHTML = `
        <div class="result premium-brief">
            <span class="badge ${badgeClass(data.level)}">${localSafeValue(data.level, "STABILE")}</span>
            <h3>Oracle Score ${localSafeNumber(data.oracle_score)}/100</h3>
            ${progressBar(localSafeNumber(data.oracle_score))}
            <h4>📌 Sintesi</h4>
            <ul>${localSafeArray(data.brief).map(x => `<li>${x}</li>`).join("")}</ul>
            <h4>🎯 Priorità</h4>
            <ul>${localSafeArray(data.priorities).map(x => `<li>${x}</li>`).join("")}</ul>
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
