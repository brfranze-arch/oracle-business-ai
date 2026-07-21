function renderCustomer() {
    setPageTitle("Clienti · Oracle AI");

    setContent(`
        <div class="card">
            <h2>👥 Clienti · Oracle AI</h2>
            <p>Clienti, concentrazione fatturato e customer intelligence.</p>

            <div class="grid-2">
                <div>
                    <h3>Crea cliente</h3>
                    <input id="customerName" placeholder="Nome cliente">
                    <input id="customerEmail" placeholder="Email">
                    <input id="customerPhone" placeholder="Telefono">
                    <input id="customerType" placeholder="Tipo cliente">
                    <textarea id="customerNotes" placeholder="Note"></textarea>
                    <button onclick="createCustomer()">Crea cliente</button>
                </div>

                <div>
                    <h3>Azioni Clienti</h3>
                    <button onclick="loadCustomers()">Carica clienti</button>
                    <button onclick="analyzeCustomerAi()">Analisi Customer AI</button>
                    <button onclick="loadCustomerInsights()">Insights salvati</button>
                </div>
            </div>

            <div id="customerResult"></div>
        </div>
    `);
}

async function createCustomer() {
    const companyId = getCompanyId();

    const params = new URLSearchParams({
        company_id: companyId,
        name: document.getElementById("customerName").value || "Cliente senza nome",
        email: document.getElementById("customerEmail").value || "",
        phone: document.getElementById("customerPhone").value || "",
        customer_type: document.getElementById("customerType").value || "generico",
        notes: document.getElementById("customerNotes").value || ""
    });

    const res = await fetch(`${API}/api/customers?${params}`, {
        method: "POST",
        headers: authHeaders()
    });

    const data = await res.json();

    if (data.error) {
        showError("customerResult", data.error);
        return;
    }

    document.getElementById("customerResult").innerHTML = `
        <div class="result">
            Cliente creato.<br>
            ID: <b>${safeValue(data.id)}</b><br>
            Nome: ${safeValue(data.name)}<br>
            Tipo: ${safeValue(data.customer_type)}
        </div>
    `;
}

async function loadCustomers() {
    const companyId = getCompanyId();
    const data = await apiGet(`/api/customers/${companyId}`);

    if (data.error) {
        showError("customerResult", data.error);
        return;
    }

    const customers = safeArray(data);

    document.getElementById("customerResult").innerHTML = `
        <div class="card">
            <h3>Clienti</h3>
            ${
                customers.length > 0
                    ? customers.map(c => `
                        <div class="result">
                            <span class="badge badge-blue">ID ${safeValue(c.id)}</span>
                            <b>${safeValue(c.name)}</b><br>
                            Email: ${safeValue(c.email)}<br>
                            Telefono: ${safeValue(c.phone)}<br>
                            Tipo: ${safeValue(c.customer_type)}<br>
                            Note: ${safeValue(c.notes)}
                        </div>
                    `).join("")
                    : "<p>Nessun cliente presente.</p>"
            }
        </div>
    `;
}

async function analyzeCustomerAi() {
    const companyId = getCompanyId();
    const data = await apiPost(`/api/customer-ai/${companyId}`);

    if (data.error) {
        showError("customerResult", data.error);
        return;
    }

    const score = safeNumber(data.customer_score);
    const level = safeValue(data.level, "STABILE");

    document.getElementById("customerResult").innerHTML = `
        <div class="card">
            <h3>Clienti · Oracle AI</h3>

            <span class="badge ${badgeClass(level)}">${level}</span>

            <div class="kpi-value">${score}/100</div>
            ${progressBar(score)}

            <div class="kpi-grid">
                <div class="kpi">
                    <div class="kpi-title">Clienti</div>
                    <div class="kpi-value">${safeNumber(data.customers_count)}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Top Cliente</div>
                    <div class="kpi-value" style="font-size:22px;">${safeValue(data.top_customer_name)}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Fatturato Top</div>
                    <div class="kpi-value">€${safeNumber(data.top_customer_revenue)}</div>
                </div>
            </div>

            <div class="result">
                <h3>Analisi AI</h3>
                <p>${safeValue(data.message, "Nessuna analisi disponibile.")}</p>
            </div>

            <div class="result">
                <h3>Raccomandazione</h3>
                <p>${safeValue(data.recommendation, "Nessuna raccomandazione disponibile.")}</p>
            </div>
        </div>
    `;
}

async function loadCustomerInsights() {
    const companyId = getCompanyId();
    const data = await apiGet(`/api/customer-insights/${companyId}`);

    if (data.error) {
        showError("customerResult", data.error);
        return;
    }

    const insights = safeArray(data);

    document.getElementById("customerResult").innerHTML = `
        <div class="card">
            <h3>Customer Insights</h3>
            ${
                insights.length > 0
                    ? insights.map(i => `
                        <div class="result">
                            <span class="badge ${badgeClass(i.level)}">${safeValue(i.level)}</span>
                            <b>Score: ${safeNumber(i.customer_score)}/100</b><br>
                            Clienti: ${safeNumber(i.customers_count)}<br>
                            Top cliente: ${safeValue(i.top_customer_name)}<br>
                            Fatturato top: €${safeNumber(i.top_customer_revenue)}<br>
                            Data: ${safeValue(i.created_at)}<br><br>
                            <b>Messaggio:</b>
                            <p>${safeValue(i.message)}</p>
                            <b>Raccomandazione:</b>
                            <p>${safeValue(i.recommendation)}</p>
                        </div>
                    `).join("")
                    : "<p>Nessun insight customer disponibile.</p>"
            }
        </div>
    `;
}