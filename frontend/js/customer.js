function renderCustomer() {
    setPageTitle("Customer Oracle AI");

    setContent(`
        <div class="card">
            <h2>👥 Customer Oracle AI</h2>
            <p>Gestione clienti, valore cliente, concentrazione fatturato e analisi AI.</p>

            <div class="grid-2">
                <div>
                    <h3>Crea cliente</h3>
                    <input id="customerName" placeholder="Nome cliente">
                    <input id="customerEmail" placeholder="Email">
                    <input id="customerPhone" placeholder="Telefono">
                    <input id="customerType" placeholder="Tipo cliente: privato, business, premium">
                    <textarea id="customerNotes" placeholder="Note"></textarea>
                    <button onclick="createCustomer()">Crea cliente</button>
                </div>

                <div>
                    <h3>Analisi clienti</h3>
                    <button onclick="loadCustomers()">Carica clienti</button>
                    <button onclick="analyzeCustomerAi()">Analizza clienti con AI</button>
                    <button onclick="loadCustomerInsights()">Carica insights clienti</button>
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
        name: document.getElementById("customerName").value,
        email: document.getElementById("customerEmail").value,
        phone: document.getElementById("customerPhone").value,
        customer_type: document.getElementById("customerType").value,
        notes: document.getElementById("customerNotes").value
    });

    const res = await fetch(`${API}/api/customers?${params}`, {
        method: "POST",
        headers: authHeaders()
    });

    const data = await res.json();

    document.getElementById("customerResult").innerHTML = `
        <div class="result">
            Cliente creato.<br>
            ID: <b>${data.id}</b><br>
            Nome: ${data.name}<br>
            Tipo: ${data.customer_type || "-"}
        </div>
    `;
}

async function loadCustomers() {
    const companyId = getCompanyId();

    const data = await apiGet(`/api/customers/${companyId}`);

    if (!Array.isArray(data)) {
        document.getElementById("customerResult").innerHTML =
            `<div class="result">${data.error || "Errore caricamento clienti"}</div>`;
        return;
    }

    document.getElementById("customerResult").innerHTML = `
        <div class="card">
            <h3>Lista clienti</h3>
            ${
                data.length > 0
                    ? data.map(c => `
                        <div class="result">
                            <span class="badge badge-blue">ID ${c.id}</span>
                            <b>${c.name}</b><br>
                            Email: ${c.email || "-"}<br>
                            Telefono: ${c.phone || "-"}<br>
                            Tipo: ${c.customer_type || "-"}<br>
                            Note: ${c.notes || "-"}
                        </div>
                    `).join("")
                    : "<p>Nessun cliente registrato.</p>"
            }
        </div>
    `;
}

async function analyzeCustomerAi() {
    const companyId = getCompanyId();

    const data = await apiPost(`/api/customer-ai/${companyId}`);

    if (data.error) {
        document.getElementById("customerResult").innerHTML =
            `<div class="result">${data.error}</div>`;
        return;
    }

    document.getElementById("customerResult").innerHTML = `
        <div class="card">
            <h3>Customer Oracle AI</h3>

            <span class="badge ${badgeClass(data.level)}">${data.level}</span>

            <div class="kpi-value">${data.customer_score}/100</div>
            ${progressBar(data.customer_score)}

            <div class="kpi-grid">
                <div class="kpi">
                    <div class="kpi-title">Clienti registrati</div>
                    <div class="kpi-value">${data.customers_count}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Top cliente</div>
                    <div class="kpi-value" style="font-size:22px;">${data.top_customer_name || "-"}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Fatturato top cliente</div>
                    <div class="kpi-value">€${data.top_customer_revenue}</div>
                </div>
            </div>

            <div class="result">
                <h3>Analisi AI</h3>
                <p>${data.message}</p>
            </div>

            <div class="result">
                <h3>Raccomandazione</h3>
                <p>${data.recommendation}</p>
            </div>
        </div>
    `;
}

async function loadCustomerInsights() {
    const companyId = getCompanyId();

    const data = await apiGet(`/api/customer-insights/${companyId}`);

    if (!Array.isArray(data)) {
        document.getElementById("customerResult").innerHTML =
            `<div class="result">${data.error || "Errore caricamento insights"}</div>`;
        return;
    }

    document.getElementById("customerResult").innerHTML = `
        <div class="card">
            <h3>Customer Insights salvati</h3>
            ${
                data.length > 0
                    ? data.map(i => `
                        <div class="result">
                            <span class="badge ${badgeClass(i.level)}">${i.level}</span>
                            <b>Customer Score: ${i.customer_score}/100</b><br>
                            Clienti: ${i.customers_count}<br>
                            Top cliente: ${i.top_customer_name || "-"}<br>
                            Fatturato top cliente: €${i.top_customer_revenue}<br>
                            Creato il: ${i.created_at}<br><br>
                            <b>Messaggio:</b>
                            <p>${i.message}</p>
                            <b>Raccomandazione:</b>
                            <p>${i.recommendation}</p>
                        </div>
                    `).join("")
                    : "<p>Nessun insight cliente ancora presente.</p>"
            }
        </div>
    `;
}