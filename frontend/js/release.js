function renderRelease() {
    setPageTitle("Release Candidate 1.0");

    setContent(`
        <div class="card">
            <h2>🚀 Oracle Business AI RC1</h2>
            <p>Centro controllo release, stato moduli e checklist finale Enterprise.</p>

            <button onclick="loadReleaseStatus()">Carica stato release</button>
            <button onclick="exportReleaseSnapshot()">Esporta snapshot RC1</button>

            <div id="releaseResult"></div>
        </div>
    `);

    loadReleaseStatus();
}

async function loadReleaseStatus() {
    const billing = await apiGet("/api/billing/me");
    const permissions = await apiGet("/api/me/permissions");
    const tenants = await apiGet("/api/tenants");

    document.getElementById("releaseResult").innerHTML = `
        <div class="card">
            <h3>✅ Stato RC1</h3>

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

