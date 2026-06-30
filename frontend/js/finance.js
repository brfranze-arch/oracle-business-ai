function renderFinance() {
    setPageTitle("Finance Oracle AI");

    setContent(`
        <div class="card">
            <h2>💰 Finance Oracle AI</h2>
            <p>Gestione entrate, metodi di pagamento e analisi finanziaria AI.</p>

            <div class="grid-2">
                <div>
                    <h3>Registra entrata</h3>
                    <input id="revenueAmount" type="number" placeholder="Importo">
                    <input id="revenueCustomerId" placeholder="ID cliente opzionale">
                    <select id="revenuePayment">
                        <option value="contanti">Contanti</option>
                        <option value="pos">POS</option>
                        <option value="bonifico">Bonifico</option>
                        <option value="digitale">Digitale</option>
                    </select>
                    <input id="revenueCategory" placeholder="Categoria">
                    <textarea id="revenueNote" placeholder="Nota"></textarea>
                    <button onclick="addRevenue()">Aggiungi entrata</button>
                </div>

                <div>
                    <h3>Analisi Finance</h3>
                    <button onclick="loadFinanceSummary()">Riepilogo entrate</button>
                    <button onclick="analyzeFinance()">Analisi AI Finance</button>
                    <button onclick="loadOracleScoreFinance()">Aggiorna Oracle Score</button>
                </div>
            </div>

            <div id="financeResult"></div>
        </div>
    `);
}

async function addRevenue() {
    const companyId = getCompanyId();

    const params = new URLSearchParams({
        company_id: companyId,
        amount: document.getElementById("revenueAmount").value,
        payment_method: document.getElementById("revenuePayment").value,
        category: document.getElementById("revenueCategory").value,
        customer_id: document.getElementById("revenueCustomerId").value || "",
        note: document.getElementById("revenueNote").value
    });

    const res = await fetch(`${API}/api/revenues?${params}`, {
        method: "POST",
        headers: authHeaders()
    });

    const data = await res.json();

    document.getElementById("financeResult").innerHTML = `
        <div class="result">
            Entrata registrata: <b>€${data.amount}</b><br>
            Metodo: ${data.payment_method}<br>
            Categoria: ${data.category}
        </div>
    `;
}

async function loadFinanceSummary() {
    const companyId = getCompanyId();
    const data = await apiGet(`/api/finance-summary/${companyId}`);

    document.getElementById("financeResult").innerHTML = `
        <div class="card">
            <h3>Riepilogo Finance</h3>

            <div class="kpi-grid">
                <div class="kpi">
                    <div class="kpi-title">Totale</div>
                    <div class="kpi-value">€${data.total}</div>
                </div>
                <div class="kpi">
                    <div class="kpi-title">Contanti</div>
                    <div class="kpi-value">€${data.cash}</div>
                </div>
                <div class="kpi">
                    <div class="kpi-title">POS</div>
                    <div class="kpi-value">€${data.pos}</div>
                </div>
                <div class="kpi">
                    <div class="kpi-title">Bonifico</div>
                    <div class="kpi-value">€${data.bank}</div>
                </div>
                <div class="kpi">
                    <div class="kpi-title">Digitale</div>
                    <div class="kpi-value">€${data.digital}</div>
                </div>
                <div class="kpi">
                    <div class="kpi-title">Operazioni</div>
                    <div class="kpi-value">${data.count}</div>
                </div>
            </div>
        </div>
    `;
}

async function analyzeFinance() {
    const companyId = getCompanyId();

    const data = await apiPost(`/api/ai/analyze-finance/${companyId}`);

    if (data.error) {
        document.getElementById("financeResult").innerHTML =
            `<div class="result">${data.error}</div>`;
        return;
    }

    document.getElementById("financeResult").innerHTML = `
        <div class="card">
            <h3>${data.title}</h3>
            <span class="badge ${badgeClass(data.level)}">${data.level}</span>

            <div class="kpi-value">${data.score}/100</div>
            ${progressBar(data.score)}

            <p>${data.message}</p>
        </div>
    `;
}

async function loadOracleScoreFinance() {
    const companyId = getCompanyId();
    const data = await apiGet(`/api/oracle-score/${companyId}`);

    document.getElementById("financeResult").innerHTML = `
        <div class="card">
            <h3>Oracle Score aggiornato</h3>
            <span class="badge ${badgeClass(data.level)}">${data.level}</span>
            <div class="kpi-value">${data.oracle_score}/100</div>
            ${progressBar(data.oracle_score)}

            <p>Finance Score: <b>${data.finance_score}</b></p>
            ${progressBar(data.finance_score)}
        </div>
    `;
}