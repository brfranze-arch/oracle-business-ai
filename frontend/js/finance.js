function renderFinance() {
    setPageTitle("Finanza · Oracle AI");

    setContent(`
        <div class="card">
            <h2>💰 Finanza · Oracle AI</h2>
            <p>Entrate, metodi di pagamento, riepilogo finanziario e analisi AI.</p>

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
                    <h3>Azioni Finanza</h3>
                    <button onclick="loadFinanceSummary()">Riepilogo entrate</button>
                    <button onclick="analyzeFinance()">Analisi AI Finanza</button>
                    <button onclick="loadOracleScoreFinance()">Oracle Score</button>
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
        amount: document.getElementById("revenueAmount").value || 0,
        payment_method: document.getElementById("revenuePayment").value,
        category: document.getElementById("revenueCategory").value || "generale",
        customer_id: document.getElementById("revenueCustomerId").value || "",
        note: document.getElementById("revenueNote").value || ""
    });

    const res = await fetch(`${API}/api/revenues?${params}`, {
        method: "POST",
        headers: authHeaders()
    });

    const data = await res.json();

    if (data.error) {
        showError("financeResult", data.error);
        return;
    }

    document.getElementById("financeResult").innerHTML = `
        <div class="result">
            Entrata registrata.<br>
            ID: <b>${safeValue(data.id)}</b><br>
            Importo: <b>€${safeNumber(data.amount)}</b><br>
            Metodo: ${safeValue(data.payment_method)}<br>
            Categoria: ${safeValue(data.category)}
        </div>
    `;
}

async function loadFinanceSummary() {
    const companyId = getCompanyId();
    const data = await apiGet(`/api/finance-summary/${companyId}`);

    if (data.error) {
        showError("financeResult", data.error);
        return;
    }

    const total = safeNumber(data.total);
    const cash = safeNumber(data.cash);
    const pos = safeNumber(data.pos);
    const bank = safeNumber(data.bank);
    const digital = safeNumber(data.digital);
    const count = safeNumber(data.count);

    document.getElementById("financeResult").innerHTML = `
        <div class="card">
            <h3>Riepilogo Finanziario</h3>

            <div class="kpi-grid">
                <div class="kpi">
                    <div class="kpi-title">Totale</div>
                    <div class="kpi-value">€${total}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Contanti</div>
                    <div class="kpi-value">€${cash}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">POS</div>
                    <div class="kpi-value">€${pos}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Bonifico</div>
                    <div class="kpi-value">€${bank}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Digitale</div>
                    <div class="kpi-value">€${digital}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Operazioni</div>
                    <div class="kpi-value">${count}</div>
                </div>
            </div>
        </div>
    `;
}

async function analyzeFinance() {
    const companyId = getCompanyId();
    const data = await apiPost(`/api/ai/analyze-finance/${companyId}`);

    if (data.error) {
        showError("financeResult", data.error);
        return;
    }

    const score = safeNumber(data.score);
    const level = safeValue(data.level, "STABILE");

    document.getElementById("financeResult").innerHTML = `
        <div class="card">
            <h3>${safeValue(data.title, "Analisi Finance AI")}</h3>

            <span class="badge ${badgeClass(level)}">${level}</span>

            <div class="kpi-value">${score}/100</div>
            ${progressBar(score)}

            <div class="result">
                ${safeValue(data.message, "Nessun messaggio AI disponibile.")}
            </div>
        </div>
    `;
}

async function loadOracleScoreFinance() {
    const companyId = getCompanyId();
    const data = await apiGet(`/api/oracle-score/${companyId}`);

    if (data.error) {
        showError("financeResult", data.error);
        return;
    }

    const oracleScore = safeNumber(data.oracle_score);
    const financeScore = safeNumber(data.finance_score);
    const level = safeValue(data.level, "STABILE");

    document.getElementById("financeResult").innerHTML = `
        <div class="card">
            <h3>Oracle Score aggiornato</h3>

            <span class="badge ${badgeClass(level)}">${level}</span>

            <div class="kpi-value">${oracleScore}/100</div>
            ${progressBar(oracleScore)}

            <div class="result">
                <h3>Punteggio Finanza</h3>
                <b>${financeScore}/100</b>
                ${progressBar(financeScore)}
            </div>
        </div>
    `;
}