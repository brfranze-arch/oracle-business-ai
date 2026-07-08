function dashboardSafeValue(value, fallback = "N/D") {
    if (value === undefined || value === null || value === "" || Number.isNaN(value)) return fallback;
    return value;
}

function dashboardSafeNumber(value, fallback = 0) {
    const n = Number(value);
    return Number.isFinite(n) ? n : fallback;
}

function dashboardSafeArray(value) {
    return Array.isArray(value) ? value : [];
}

function normalizeExecutiveData(data) {
    return {
        company_name: dashboardSafeValue(data.company_name, "Azienda"),
        oracle_score: dashboardSafeNumber(data.oracle_score),
        oracle_level: dashboardSafeValue(data.oracle_level || data.level, "STABILE"),
        total_revenue: dashboardSafeNumber(data.total_revenue),
        operations: dashboardSafeNumber(data.operations || data.total_operations || data.count),
        customers: dashboardSafeNumber(data.customers || data.customers_count),
        top_customer: dashboardSafeValue(data.top_customer || data.top_customer_name, "N/D"),
        compliance_items: dashboardSafeNumber(data.compliance_items || data.total_items),
        cyber_score: dashboardSafeNumber(data.cyber_score, 50),
        attack_probability_30d: dashboardSafeNumber(data.attack_probability_30d),
        attack_probability_90d: dashboardSafeNumber(data.attack_probability_90d),
        suggestions: dashboardSafeArray(data.suggestions),
        risks: dashboardSafeArray(data.risks)
    };
}

async function safeDashboardGet(url, fallback = null) {
    try {
        const data = await apiGet(url);
        if (!data || data.error) return fallback;
        return data;
    } catch (e) {
        return fallback;
    }
}

async function renderDashboard() {
    setPageTitle("Executive Dashboard");

    setContent(`
        <div class="enterprise-dashboard-shell">
            <div class="executive-hero-v2">
                <div>
                    <div class="eyebrow">Oracle Business AI 1.0</div>
                    <h1>Executive Command Center</h1>
                    <p>Digital twin aziendale, AI advisor, rischio cyber, finance, customer e compliance in un'unica vista decisionale.</p>
                </div>
                <div class="hero-actions-v2">
                    <button onclick="loadExecutiveDashboard()">Aggiorna Command Center</button>
                    <button onclick="loadDailyBrief()">Daily Brief</button>
                </div>
            </div>

            <div id="dashboardResult">
                <div class="card loading-card">
                    <h2>🚀 Caricamento Executive Intelligence...</h2>
                    <p>Sto consolidando KPI, rischi, timeline e suggerimenti AI.</p>
                </div>
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

    const [dailyBrief, predictiveHistory, agentsHistory, openaiUsage, billingMe, osintScans] = await Promise.all([
        safeDashboardGet(`/api/daily-brief/${companyId}`, null),
        safeDashboardGet(`/api/predictive/history/${companyId}`, []),
        safeDashboardGet(`/api/agents/history/${companyId}`, []),
        safeDashboardGet(`/api/openai/usage/${companyId}`, []),
        safeDashboardGet(`/api/billing/me`, null),
        safeDashboardGet(`/api/osint/scans/${companyId}`, [])
    ]);

    const predictiveLatest = dashboardSafeArray(predictiveHistory)[0] || null;
    const agents = dashboardSafeArray(agentsHistory).slice(0, 5);
    const openaiLast = dashboardSafeArray(openaiUsage)[0] || null;
    const osintLast = dashboardSafeArray(osintScans)[0] || null;
    const plan = billingMe ? dashboardSafeValue(billingMe.plan, "FREE") : "N/D";
    const predictionScore = predictiveLatest ? dashboardSafeNumber(predictiveLatest.prediction_score) : Math.round((data.oracle_score + data.cyber_score) / 2);
    const confidence = calculateAIConfidence(data, predictiveLatest, agents, openaiLast);

    if (typeof buildNotifications === "function" && typeof renderNotificationCenter === "function") {
        renderNotificationCenter(buildEnterpriseNotifications(data, predictiveLatest, agents, plan));
    }

    document.getElementById("dashboardResult").innerHTML = `
        <div class="executive-summary-panel">
            <div>
                <span class="badge ${badgeClass(data.oracle_level)}">${data.oracle_level}</span>
                <h2>${data.company_name}</h2>
                <p>${buildExecutiveSummaryText(data, predictiveLatest, agents)}</p>
            </div>
            <div class="ai-confidence-card">
                <span>AI Confidence</span>
                <strong class="counter" data-target="${confidence}">0</strong>
                ${progressBar(confidence)}
            </div>
        </div>

        ${renderLiveStatus(data, predictiveLatest, plan, osintLast)}

        <div class="kpi-grid enterprise-kpis-v2">
            ${renderExecutiveKpi("🏆", "Oracle Score", data.oracle_score, "/100", data.oracle_level, progressBar(data.oracle_score))}
            ${renderExecutiveKpi("💰", "Revenue", data.total_revenue, "€", `${data.operations} operazioni`, "")}
            ${renderExecutiveKpi("👥", "Customer", data.customers, "", `Top: ${data.top_customer}`, "")}
            ${renderExecutiveKpi("📄", "Compliance", data.compliance_items, "item", "Documenti e scadenze", progressBar(Math.max(0, 100 - data.compliance_items * 5)))}
            ${renderExecutiveKpi("🛡", "Cyber Score", data.cyber_score, "/100", `30d ${data.attack_probability_30d}%`, progressBar(data.cyber_score))}
            ${renderExecutiveKpi("🔮", "Predictive", predictionScore, "/100", predictiveLatest ? dashboardSafeValue(predictiveLatest.level) : "Baseline", progressBar(predictionScore))}
            ${renderExecutiveKpi("🤖", "Agents", agents.length, "run", agents.length ? "Ultime attività" : "Nessun run", "")}
            ${renderExecutiveKpi("💳", "Plan", 0, "", plan, renderPlanChip(plan))}
        </div>

        <div class="grid-2 enterprise-grid-v2">
            <div class="card executive-brief-card">
                <h2>🧠 Executive AI Summary</h2>
                ${renderDailyBriefInline(dailyBrief, data)}
            </div>

            <div class="card decision-center-card">
                <h2>🎯 Decision Center</h2>
                ${renderDecisionCenter(data)}
            </div>
        </div>

        <div class="grid-2 enterprise-grid-v2">
            <div class="card">
                <h2>🕒 Live Timeline</h2>
                ${renderLiveTimeline(data, predictiveLatest, agents, openaiLast, osintLast, plan)}
            </div>

            <div class="card">
                <h2>⚡ Quick Actions</h2>
                <div class="quick-action-grid">
                    <button onclick="showPage('reports')">📊 Reports</button>
                    <button onclick="showPage('assistant')">🤖 AI Advisor</button>
                    <button onclick="showPage('cyber')">🛡 Cyber</button>
                    <button onclick="showPage('billing')">💳 Billing</button>
                    <button onclick="showPage('settings')">⚙️ Workspace</button>
                    <button onclick="showPage('import')">📂 Import</button>
                </div>
            </div>
        </div>

        <div class="card enterprise-footer-panel">
            <h2>📈 Enterprise Intelligence Index</h2>
            <div class="index-row">
                <div><span>Decision Quality</span><strong>${Math.round((data.oracle_score + confidence) / 2)}/100</strong></div>
                <div><span>Business Health</span><strong>${data.oracle_score}/100</strong></div>
                <div><span>Risk Control</span><strong>${Math.max(0, 100 - data.attack_probability_30d)}/100</strong></div>
                <div><span>Data Depth</span><strong>${Math.min(100, data.operations * 8 + data.customers * 5)}/100</strong></div>
            </div>
        </div>
    `;

    setPageTitle("Executive Dashboard ✓ aggiornato");
    animateCounters();
}

function calculateAIConfidence(data, predictiveLatest, agents, openaiLast) {
    let score = 55;
    if (data.operations > 0) score += 12;
    if (data.customers > 0) score += 10;
    if (data.compliance_items > 0) score += 8;
    if (predictiveLatest) score += 8;
    if (agents.length > 0) score += 5;
    if (openaiLast) score += 2;
    return Math.min(98, score);
}

function buildExecutiveSummaryText(data, predictiveLatest, agents) {
    const riskCount = data.risks.length;
    const actionCount = data.suggestions.length;
    const predictive = predictiveLatest ? ` Predictive AI: ${dashboardSafeValue(predictiveLatest.level)}.` : "";
    const agentsText = agents.length ? ` ${agents.length} agenti hanno prodotto attività recenti.` : "";
    return `Oracle Score ${data.oracle_score}/100. Rischi rilevati: ${riskCount}. Azioni AI consigliate: ${actionCount}.${predictive}${agentsText}`;
}

function renderExecutiveKpi(icon, title, value, suffix, caption, extra) {
    const numeric = dashboardSafeNumber(value);
    const valueHtml = suffix === "€" ? `€${numeric}` : suffix ? `${numeric}${suffix}` : `${caption}`;
    return `
        <div class="kpi enterprise-kpi-v2">
            <div class="kpi-icon-v2">${icon}</div>
            <div class="kpi-title">${title}</div>
            <div class="kpi-value ${suffix !== "" && suffix !== "item" ? "counter" : ""}" data-target="${numeric}">${valueHtml}</div>
            <span class="kpi-caption-v2">${caption}</span>
            ${extra || ""}
        </div>
    `;
}

function renderPlanChip(plan) {
    const p = dashboardSafeValue(plan, "FREE").toUpperCase();
    return `<span class="plan-chip plan-${p.toLowerCase()}">${p}</span>`;
}

function renderLiveStatus(data, predictiveLatest, plan, osintLast) {
    const items = [
        ["Finance", data.operations > 0 ? "online" : "warning", data.operations > 0 ? "Dati presenti" : "Pochi dati"],
        ["Customer", data.customers > 0 ? "online" : "warning", data.customers > 0 ? "Clienti attivi" : "Da popolare"],
        ["Compliance", data.compliance_items > 0 ? "online" : "warning", data.compliance_items > 0 ? "Monitorata" : "Da configurare"],
        ["Cyber", data.cyber_score >= 55 ? "online" : "danger", `${data.cyber_score}/100`],
        ["Predictive", predictiveLatest ? "online" : "warning", predictiveLatest ? "Attivo" : "Baseline"],
        ["OSINT", osintLast ? "online" : "warning", osintLast ? "Scan presente" : "Da eseguire"],
        ["Billing", plan !== "N/D" ? "online" : "warning", plan]
    ];

    return `
        <div class="live-status-bar">
            ${items.map(i => `
                <div class="live-status-item ${i[1]}">
                    <span class="status-dot"></span>
                    <strong>${i[0]}</strong>
                    <small>${i[2]}</small>
                </div>
            `).join("")}
        </div>
    `;
}

function renderDailyBriefInline(dailyBrief, data) {
    if (!dailyBrief) {
        return `
            <p>Daily Brief automatico non disponibile. Puoi generarlo manualmente.</p>
            <button onclick="loadDailyBrief()">Genera Daily Brief</button>
            <div id="dailyBriefInline"></div>
        `;
    }

    const brief = dashboardSafeArray(dailyBrief.brief);
    const priorities = dashboardSafeArray(dailyBrief.priorities);
    return `
        <span class="badge ${badgeClass(dailyBrief.level || data.oracle_level)}">${dashboardSafeValue(dailyBrief.level || data.oracle_level)}</span>
        <h3>Oracle Score ${dashboardSafeNumber(dailyBrief.oracle_score || data.oracle_score)}/100</h3>
        ${progressBar(dashboardSafeNumber(dailyBrief.oracle_score || data.oracle_score))}
        <h4>📌 Sintesi</h4>
        <ul>${brief.slice(0, 4).map(x => `<li>${x}</li>`).join("")}</ul>
        <h4>🎯 Priorità</h4>
        <ul>${priorities.slice(0, 4).map(x => `<li>${x}</li>`).join("")}</ul>
        <div id="dailyBriefInline"></div>
    `;
}

function renderDecisionCenter(data) {
    const suggestions = dashboardSafeArray(data.suggestions).slice(0, 5);
    const risks = dashboardSafeArray(data.risks).slice(0, 5);
    return `
        <div class="decision-columns">
            <div>
                <h3>Azioni consigliate</h3>
                ${suggestions.length ? suggestions.map(x => `<div class="action-item"><span>🎯</span><p>${x}</p></div>`).join("") : "<p>Nessuna azione urgente.</p>"}
            </div>
            <div>
                <h3>Rischi</h3>
                ${risks.length ? risks.map(x => `<div class="risk-item"><span>⚠️</span><p>${x}</p></div>`).join("") : "<p>Nessun rischio importante rilevato.</p>"}
            </div>
        </div>
    `;
}

function renderLiveTimeline(data, predictiveLatest, agents, openaiLast, osintLast, plan) {
    const events = [];
    events.push(["Executive", `Dashboard aggiornata per ${data.company_name}.`, "now"]);
    events.push(["Finance", `${data.operations} operazioni, revenue totale €${data.total_revenue}.`, "finance"]);
    events.push(["Cyber", `Cyber Score ${data.cyber_score}/100, rischio 30 giorni ${data.attack_probability_30d}%.`, "cyber"]);
    if (predictiveLatest) events.push(["Predictive", `Prediction Score ${dashboardSafeNumber(predictiveLatest.prediction_score)}/100.`, "predictive"]);
    if (agents.length) events.push(["Agents", `${agents.length} attività agenti recenti disponibili.`, "agents"]);
    if (openaiLast) events.push(["OpenAI", `Ultima richiesta AI: ${dashboardSafeValue(openaiLast.question).slice(0, 80)}...`, "openai"]);
    if (osintLast) events.push(["OSINT", `Ultimo scan: ${dashboardSafeValue(osintLast.domain)} exposure ${dashboardSafeNumber(osintLast.exposure_score)}/100.`, "osint"]);
    events.push(["Billing", `Piano attuale: ${plan}.`, "billing"]);

    return `
        <div class="live-timeline-v2">
            ${events.map(e => `
                <div class="timeline-row-v2 ${e[2]}">
                    <span></span>
                    <div><strong>${e[0]}</strong><p>${e[1]}</p></div>
                </div>
            `).join("")}
        </div>
    `;
}

function buildEnterpriseNotifications(data, predictiveLatest, agents, plan) {
    const notifications = [];
    if (data.oracle_score < 65) notifications.push({ type: "warning", icon: "⚠️", text: "Oracle Score sotto la soglia FORTE." });
    if (data.attack_probability_30d > 25) notifications.push({ type: "danger", icon: "🛡", text: `Rischio cyber 30 giorni: ${data.attack_probability_30d}%.` });
    if (data.risks.length) notifications.push({ type: "warning", icon: "🚨", text: `${data.risks.length} rischi aziendali rilevati.` });
    if (data.suggestions.length) notifications.push({ type: "info", icon: "🤖", text: `${data.suggestions.length} azioni AI consigliate.` });
    if (predictiveLatest && dashboardSafeNumber(predictiveLatest.prediction_score) < 55) notifications.push({ type: "warning", icon: "🔮", text: "Predictive AI segnala attenzione operativa." });
    if (agents.some(a => dashboardSafeValue(a.priority).toLowerCase() === "high")) notifications.push({ type: "danger", icon: "🤖", text: "Autonomous Agents hanno priorità alta." });
    if (plan === "FREE") notifications.push({ type: "info", icon: "💳", text: "Piano FREE attivo: alcune funzioni enterprise sono bloccate." });
    if (!notifications.length) notifications.push({ type: "success", icon: "✅", text: "Nessuna criticità importante rilevata." });
    return notifications;
}

async function loadDailyBrief() {
    const companyId = getCompanyId();
    const data = await apiGet(`/api/daily-brief/${companyId}`);

    if (data.error) {
        document.getElementById("dailyBriefInline").innerHTML = `<div class="result">${data.error}</div>`;
        return;
    }

    document.getElementById("dailyBriefInline").innerHTML = `
        <div class="result">
            <span class="badge ${badgeClass(data.level)}">${dashboardSafeValue(data.level, "STABILE")}</span>
            <h3>Oracle Score ${dashboardSafeNumber(data.oracle_score)}/100</h3>
            ${progressBar(dashboardSafeNumber(data.oracle_score))}
            <h4>📌 Sintesi</h4>
            <ul>${dashboardSafeArray(data.brief).map(x => `<li>${x}</li>`).join("")}</ul>
            <h4>🎯 Priorità</h4>
            <ul>${dashboardSafeArray(data.priorities).map(x => `<li>${x}</li>`).join("")}</ul>
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
            if (el.innerText.includes("€")) {
                el.innerText = `€${Math.round(current * 100) / 100}`;
            } else if (el.innerText.includes("/100")) {
                el.innerText = `${Math.round(current * 100) / 100}/100`;
            } else {
                el.innerText = Math.round(current * 100) / 100;
            }
        }, 20);
    });
}
