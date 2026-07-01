function renderBilling() {
    setPageTitle("Billing SaaS");

    setContent(`
        <div class="card">
            <h2>💳 Oracle Billing</h2>
            <p>Gestione piano, trial, permessi e upgrade SaaS.</p>

            <button onclick="loadBillingMe()">Carica piano attuale</button>
            <button onclick="loadBillingPlans()">Carica piani disponibili</button>

            <div id="billingResult"></div>
        </div>
    `);

    loadBillingMe();
}

async function loadBillingMe() {
    const data = await apiGet("/api/billing/me");

    if (data.error) {
        showError("billingResult", data.error);
        return;
    }

    const permissions = data.permissions || {};

    document.getElementById("billingResult").innerHTML = `
        <div class="card">
            <h3>Piano attuale</h3>

            <div class="kpi-grid">
                <div class="kpi">
                    <div class="kpi-title">Piano</div>
                    <div class="kpi-value">${safeValue(data.plan)}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Stato</div>
                    <div class="kpi-value">${safeValue(data.status)}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Trial</div>
                    <div class="kpi-value">${data.trial ? "Attivo" : "No"}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Provider</div>
                    <div class="kpi-value">${safeValue(data.provider)}</div>
                </div>
            </div>

            <div class="result">
                <h3>Scadenze</h3>
                Trial end: ${safeValue(data.trial_end)}<br>
                Rinnovo: ${safeValue(data.renewal_date)}<br>
                Cancellazione: ${safeValue(data.cancel_date)}
            </div>

            <div class="result">
                <h3>Permessi attivi</h3>
                ${renderPermissionList(permissions)}
            </div>
        </div>
    `;
}

function renderPermissionList(permissions) {
    const keys = [
        "finance",
        "customer",
        "compliance",
        "cyber",
        "assistant",
        "reports",
        "timeline",
        "import_data",
        "openai",
        "osint",
        "predictive",
        "agents",
        "multi_company",
        "pdf_export",
        "api_access"
    ];

    return keys.map(key => {
        const enabled = permissions[key] === true;

        return `
            <span class="badge ${enabled ? "badge-green" : "badge-red"}">
                ${enabled ? "✔" : "✖"} ${key}
            </span>
        `;
    }).join("");
}

async function loadBillingPlans() {
    const data = await apiGet("/api/billing/plans");

    if (data.error) {
        showError("billingResult", data.error);
        return;
    }

    const plans = safeArray(data);

    document.getElementById("billingResult").innerHTML = `
        <div class="card">
            <h3>Piani disponibili</h3>

            <div class="kpi-grid">
                ${
                    plans.map(plan => `
                        <div class="kpi">
                            <div class="kpi-title">${safeValue(plan.name)}</div>

                            <div class="kpi-value">
                                €${safeNumber(plan.price_month)}
                            </div>

                            <p>${safeValue(plan.description)}</p>

                            <p>
                                Aziende: ${safeNumber(plan.max_companies)}<br>
                                Utenti: ${safeNumber(plan.max_users)}<br>
                                Annuale: €${safeNumber(plan.price_year)}
                            </p>

                            <button onclick="changeBillingPlan('${plan.name}')">
                                Seleziona ${plan.name}
                            </button>
                        </div>
                    `).join("")
                }
            </div>
        </div>
    `;
}

async function changeBillingPlan(planName) {
    const params = new URLSearchParams({
        plan: planName
    });

    const res = await fetch(`${API}/api/billing/change-plan?${params}`, {
        method: "POST",
        headers: authHeaders()
    });

    const data = await res.json();

    if (data.error) {
        showError("billingResult", data.error);
        return;
    }

    document.getElementById("billingResult").innerHTML = `
        <div class="card">
            <h3>Piano aggiornato</h3>
            <p>${safeValue(data.message)}</p>

            <div class="result">
                Piano attuale: <b>${safeValue(data.plan)}</b>
            </div>

            <button onclick="loadBillingMe()">Ricarica Billing</button>
        </div>
    `;
}