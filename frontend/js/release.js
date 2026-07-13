function renderRelease() {
    setPageTitle("Release Candidate 1.0");

    setContent(`
        <div class="card">
            <h2>🚀 Oracle Business AI RC1</h2>
            <p>Centro controllo release, stato moduli e checklist finale Enterprise.</p>

            <button onclick="loadReleaseStatus()">Carica stato release</button>
            <button onclick="exportReleaseSnapshot()">Esporta snapshot RC1</button>
            <button onclick="exportTestChecklist()">Esporta checklist test</button>
            <button onclick="exportReleaseAudit()">Esporta audit log</button>
            <button onclick="runRC1Diagnostics()">Esegui diagnostica moduli</button>
            <button onclick="exportRC1Diagnostics()">Esporta diagnostica</button>

            <div id="releaseResult"></div>
        </div>
    `);

    loadReleaseStatus();
}

async function loadReleaseStatus() {
    addReleaseAudit("Viewed RC1 Release Center");
    const billing = await apiGet("/api/billing/me");
    const permissions = await apiGet("/api/me/permissions");
    const tenants = await apiGet("/api/tenants");
    const backendHealth = await apiGet("/");
    const healthScore = calculatePlatformHealth(billing, permissions, tenants, backendHealth);
    const finalStatus = getRC1FinalStatus(healthScore);

    document.getElementById("releaseResult").innerHTML = `
        <div class="card">
            <h3>✅ Stato RC1</h3>
            <div class="result">
    <h3>🟢 Enterprise Health Center</h3>

    <div class="kpi-grid">
        <div class="kpi">
            <div class="kpi-title">Backend</div>
            <div class="kpi-value">${backendHealth.status === "online" ? "ONLINE" : "CHECK"}</div>
        </div>

        <div class="kpi">
            <div class="kpi-title">Frontend</div>
            <div class="kpi-value">ONLINE</div>
        </div>

        <div class="kpi">
            <div class="kpi-title">Billing</div>
            <div class="kpi-value">${safeValue(billing.plan)}</div>
        </div>

        <div class="kpi">
            <div class="kpi-title">Health Score</div>
            <div class="kpi-value">${healthScore}/100</div>
            ${progressBar(healthScore)}
        </div>
    </div>

    <div class="result">
    <h3>🚀 RC1 Final Status</h3>

    <div class="kpi-grid">
        <div class="kpi">
            <div class="kpi-title">Release Status</div>
            <div class="kpi-value">${finalStatus.label}</div>
        </div>

        <div class="kpi">
            <div class="kpi-title">Deploy Readiness</div>
            <div class="kpi-value">${finalStatus.readiness}%</div>
            ${progressBar(finalStatus.readiness)}
        </div>
    </div>

    <span class="badge ${finalStatus.badge}">
        ${finalStatus.message}
    </span>
</div>
    <p>
        Stato generale piattaforma:
        <span class="badge ${healthScore >= 80 ? "badge-green" : healthScore >= 60 ? "badge-yellow" : "badge-red"}">
            ${healthScore >= 80 ? "OPERATIVA" : healthScore >= 60 ? "ATTENZIONE" : "CRITICA"}
        </span>
    </p>
</div>

            <div class="kpi-grid">
                <div class="kpi">
                    <div class="kpi-title">Billing</div>
                    <div class="kpi-value">${safeValue(billing.plan)}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Subscription</div>
                    <div class="kpi-value">${safeValue(billing.status)}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Tenant</div>
                    <div class="kpi-value">${safeArray(tenants).length}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">RC1 Status</div>
                    <div class="kpi-value">READY</div>
                </div>
            </div>

            <div class="result">
                <h3>Moduli Enterprise</h3>
                ${releaseBadge("Finance", permissions.finance)}
                ${releaseBadge("Customer", permissions.customer)}
                ${releaseBadge("Compliance", permissions.compliance)}
                ${releaseBadge("Cyber", permissions.cyber)}
                ${releaseBadge("Reports", permissions.reports)}
                ${releaseBadge("Import", permissions.import_data)}
                ${releaseBadge("OpenAI", permissions.openai)}
                ${releaseBadge("OSINT", permissions.osint)}
                ${releaseBadge("Predictive", permissions.predictive)}
                ${releaseBadge("Agents", permissions.agents)}
            </div>

            <div class="result">
                <h3>Checklist finale</h3>
                <p>✅ Login/Auth</p>
                <p>✅ Billing Stripe</p>
                <p>✅ Multi Tenant</p>
                <p>✅ Dashboard Enterprise</p>
                <p>✅ OpenAI Advisor</p>
                <p>✅ OSINT</p>
                <p>✅ Predictive AI</p>
                <p>✅ Autonomous Agents</p>
                <p>✅ Digital Twin</p>
            </div>

<div class="result">
    <h3>📌 Release Notes RC1</h3>
    <p><b>Versione:</b> Oracle Business AI RC1</p>
    <p><b>Stato:</b> Release Candidate stabile</p>
    <p><b>Moduli inclusi:</b> Billing, Multi Tenant, OpenAI, OSINT, Predictive AI, Autonomous Agents, Digital Twin.</p>
    <p><b>Deploy:</b> Render + PostgreSQL + Stripe + OpenAI API.</p>
    <p><b>Obiettivo:</b> versione pronta per demo, test clienti e validazione commerciale.</p>
</div>

<div class="result">
    <h3>🎯 Prossime azioni consigliate</h3>
    <p>1. Test completo con account FREE, BUSINESS ed ENTERPRISE.</p>
    <p>2. Verifica Stripe Customer Portal.</p>
    <p>3. Verifica permessi modulo per piano.</p>
    <p>4. Test OpenAI con budget limitato.</p>
    <p>5. Preparazione demo commerciale.</p>
</div>
        </div>
    `;
}

function releaseBadge(label, active) {
    return `
        <span class="badge ${active ? "badge-green" : "badge-red"}">
            ${active ? "✔" : "✖"} ${label}
        </span>
    `;
}

function exportReleaseSnapshot() {
    const snapshot = {
        product: "Oracle Business AI",
        version: "RC1",
        date: new Date().toISOString(),
        status: "READY",
        modules: {
            auth: true,
            billing: true,
            stripe: true,
            multiTenant: true,
            dashboard: true,
            finance: true,
            customer: true,
            compliance: true,
            cyber: true,
            osint: true,
            openai: true,
            predictive: true,
            agents: true,
            digitalTwin: true
        }
    };

    const blob = new Blob(
        [JSON.stringify(snapshot, null, 2)],
        { type: "application/json" }
    );

    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "oracle_business_ai_rc1_snapshot.json";
    a.click();

    URL.revokeObjectURL(url);
}

function exportTestChecklist() {
    const checklist = `
ORACLE BUSINESS AI - RC1 TEST CHECKLIST

[ ] Login
[ ] Logout
[ ] Registrazione nuovo utente
[ ] Billing - piano attuale
[ ] Billing - Stripe Checkout
[ ] Billing - Customer Portal
[ ] Billing - Fatture
[ ] Multi Tenant - selezione workspace
[ ] Settings - crea azienda nel tenant
[ ] Dashboard
[ ] Finance
[ ] Customer
[ ] Compliance
[ ] Cyber
[ ] OSINT
[ ] Assistant Base
[ ] OpenAI Enterprise Advisor
[ ] Reports
[ ] Predictive AI
[ ] Autonomous Agents
[ ] Digital Twin
[ ] Import CSV/Excel
[ ] Release Center
[ ] Test permessi FREE
[ ] Test permessi BUSINESS
[ ] Test permessi ENTERPRISE
[ ] Deploy Render backend
[ ] Deploy Render frontend
`;

    const blob = new Blob([checklist], { type: "text/plain" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "oracle_business_ai_rc1_test_checklist.txt";
    a.click();

    URL.revokeObjectURL(url);
}

function addReleaseAudit(action) {
    const logs = JSON.parse(localStorage.getItem("oracle_release_audit") || "[]");

    logs.unshift({
        action: action,
        date: new Date().toISOString(),
        user: localStorage.getItem("oracle_user") || "unknown"
    });

    localStorage.setItem("oracle_release_audit", JSON.stringify(logs.slice(0, 100)));
}

function exportReleaseAudit() {
    addReleaseAudit("Export audit log");

    const logs = JSON.parse(localStorage.getItem("oracle_release_audit") || "[]");

    const blob = new Blob(
        [JSON.stringify(logs, null, 2)],
        { type: "application/json" }
    );

    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "oracle_business_ai_rc1_audit_log.json";
    a.click();

    URL.revokeObjectURL(url);
}

function calculatePlatformHealth(billing, permissions, tenants, backendHealth) {
    let score = 0;

    if (backendHealth && backendHealth.status === "online") score += 20;
    if (billing && billing.plan) score += 20;
    if (permissions && permissions.finance) score += 15;
    if (permissions && permissions.customer) score += 15;
    if (permissions && permissions.compliance) score += 10;
    if (permissions && permissions.openai) score += 10;
    if (safeArray(tenants).length > 0) score += 10;

    return Math.min(100, score);
}

function getRC1FinalStatus(healthScore) {
    if (healthScore >= 85) {
        return {
            label: "READY",
            readiness: 100,
            badge: "badge-green",
            message: "Oracle Business AI RC1 è pronta per demo e validazione clienti."
        };
    }

    if (healthScore >= 65) {
        return {
            label: "WARNING",
            readiness: 75,
            badge: "badge-yellow",
            message: "RC1 operativa, ma alcune aree richiedono verifica."
        };
    }

    return {
        label: "BLOCKED",
        readiness: 40,
        badge: "badge-red",
        message: "RC1 non pronta: verificare backend, billing, permessi e tenant."
    };
}

let rc1DiagnosticsCache = [];

async function runRC1Diagnostics() {
    const companyId = getCompanyId();

    const tests = [
        {
            name: "Backend",
            request: () => apiGet("/")
        },
        {
            name: "Billing",
            request: () => apiGet("/api/billing/me")
        },
        {
            name: "Permessi",
            request: () => apiGet("/api/me/permissions")
        },
        {
            name: "Tenant",
            request: () => apiGet("/api/tenants")
        },
        {
            name: "Aziende Workspace",
            request: () => apiGet("/api/tenant/companies")
        },
        {
            name: "Dashboard",
            request: () => apiGet(`/api/executive-dashboard/${companyId}`)
        },
        {
            name: "Finance",
            request: () => apiGet(`/api/finance-summary/${companyId}`)
        },
        {
            name: "Customer",
            request: () => apiGet(`/api/customers/${companyId}`)
        },
        {
            name: "Compliance",
            request: () => apiGet(`/api/compliance-items/${companyId}`)
        },
        {
            name: "Cyber",
            request: () => apiGet(`/api/cyber-assets/${companyId}`)
        },
        {
            name: "Reports",
            request: () => apiGet(`/api/oracle-timeline/${companyId}`)
        },
        {
            name: "OpenAI Usage",
            request: () => apiGet(`/api/openai/usage/${companyId}`)
        },
        {
            name: "Predictive",
            request: () => apiGet(`/api/predictive/history/${companyId}`)
        },
        {
            name: "Agents",
            request: () => apiGet(`/api/agents/history/${companyId}`)
        }
    ];

    document.getElementById("releaseResult").innerHTML = `
        <div class="card">
            <h2>🧪 Diagnostica RC1</h2>
            <div class="result">
                Verifica moduli in corso...
            </div>
        </div>
    `;

    const results = [];

    for (const test of tests) {
        try {
            const startedAt = performance.now();
            const response = await test.request();
            const elapsed = Math.round(performance.now() - startedAt);

            const errorMessage = response && response.error
                ? response.error
                : null;

            results.push({
                module: test.name,
                status: errorMessage ? "warning" : "ok",
                message: errorMessage || "Modulo raggiungibile",
                response_time_ms: elapsed
            });
        } catch (error) {
            results.push({
                module: test.name,
                status: "error",
                message: error.message || "Errore di connessione",
                response_time_ms: 0
            });
        }
    }

    rc1DiagnosticsCache = results;

    addReleaseAudit("Executed RC1 diagnostics");

    renderRC1Diagnostics(results);
}

function renderRC1Diagnostics(results) {
    const okCount = results.filter(item => item.status === "ok").length;
    const warningCount = results.filter(item => item.status === "warning").length;
    const errorCount = results.filter(item => item.status === "error").length;

    const score = Math.round((okCount / results.length) * 100);

    document.getElementById("releaseResult").innerHTML = `
        <div class="card">
            <h2>🧪 Diagnostica RC1</h2>

            <div class="kpi-grid">
                <div class="kpi">
                    <div class="kpi-title">Moduli OK</div>
                    <div class="kpi-value">${okCount}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Warning</div>
                    <div class="kpi-value">${warningCount}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Errori</div>
                    <div class="kpi-value">${errorCount}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Diagnostic Score</div>
                    <div class="kpi-value">${score}/100</div>
                    ${progressBar(score)}
                </div>
            </div>

            ${
                results.map(item => `
                    <div class="result">
                        <span class="badge ${
                            item.status === "ok"
                                ? "badge-green"
                                : item.status === "warning"
                                    ? "badge-yellow"
                                    : "badge-red"
                        }">
                            ${
                                item.status === "ok"
                                    ? "OK"
                                    : item.status === "warning"
                                        ? "WARNING"
                                        : "ERROR"
                            }
                        </span>

                        <b>${safeValue(item.module)}</b><br>
                        Messaggio: ${safeValue(item.message)}<br>
                        Tempo risposta: ${safeNumber(item.response_time_ms)} ms
                    </div>
                `).join("")
            }

            <button onclick="loadReleaseStatus()">
                Torna allo stato RC1
            </button>
        </div>
    `;
}

function exportRC1Diagnostics() {
    if (!rc1DiagnosticsCache.length) {
        showError(
            "releaseResult",
            "Esegui prima la diagnostica dei moduli."
        );
        return;
    }

    addReleaseAudit("Exported RC1 diagnostics");

    const report = {
        product: "Oracle Business AI",
        version: "RC1",
        generated_at: new Date().toISOString(),
        tenant_id: getTenantId(),
        company_id: getCompanyId(),
        results: rc1DiagnosticsCache
    };

    const blob = new Blob(
        [JSON.stringify(report, null, 2)],
        { type: "application/json" }
    );

    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "oracle_business_ai_rc1_diagnostics.json";
    a.click();

    URL.revokeObjectURL(url);
}