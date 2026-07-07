function renderAssistant() {
    setPageTitle("Oracle Assistant AI");

    setContent(`
        <div class="card">
            <h2>🤖 Oracle Assistant AI</h2>
            <p>Assistente AI basato sui dati reali dell’azienda.</p>

            <textarea id="assistantQuestion" placeholder="Esempio: Come sta andando la mia azienda? Qual è il mio rischio cyber? Cosa devo migliorare?"></textarea>

            <button onclick="askAssistant()">Assistant Base</button>
            <button onclick="askOpenAIAdvisor()">OpenAI Enterprise Advisor</button>
            <button onclick="loadOpenAIUsage()">Storico OpenAI</button>
            <button onclick="loadAssistantMemory()">Memoria AI</button>

            <div id="assistantResult"></div>
        </div>
    `);
}

async function askAssistant() {
    const companyId = getCompanyId();
    const question = document.getElementById("assistantQuestion").value || "";

    if (!question.trim()) {
        showError("assistantResult", "Scrivi una domanda.");
        return;
    }

    const params = new URLSearchParams({ question });

    const res = await fetch(`${API}/api/oracle-assistant/${companyId}?${params}`, {
        method: "POST",
        headers: authHeaders()
    });

    const data = await res.json();

    if (data.error) {
        showError("assistantResult", data.error);
        return;
    }

    const oracle = data.oracle_score || {};
    const score = safeNumber(oracle.oracle_score);
    const level = safeValue(oracle.level, "STABILE");

    document.getElementById("assistantResult").innerHTML = `
        <div class="card">
            <h3>Risposta Oracle Assistant</h3>

            <div class="result">
                <b>Domanda:</b>
                <p>${safeValue(data.question)}</p>
            </div>

            <div class="result">
                <b>Risposta:</b>
                <pre style="white-space:pre-wrap;font-family:inherit;">${safeValue(data.answer)}</pre>
            </div>

            <div class="result">
                <h3>Oracle Score collegato</h3>
                <span class="badge ${badgeClass(level)}">${level}</span>
                <div class="kpi-value">${score}/100</div>
                ${progressBar(score)}
            </div>
        </div>
    `;
}

async function askOpenAIAdvisor() {
    const companyId = getCompanyId();
    const question = document.getElementById("assistantQuestion").value || "";

    if (!question.trim()) {
        showError("assistantResult", "Scrivi una domanda.");
        return;
    }

    const params = new URLSearchParams({ question });

    document.getElementById("assistantResult").innerHTML = `
        <div class="result">OpenAI Enterprise Advisor sta analizzando i dati aziendali...</div>
    `;

    const res = await fetch(`${API}/api/openai/company-advisor/${companyId}?${params}`, {
        method: "POST",
        headers: authHeaders()
    });

    const data = await res.json();

    if (data.error) {
        showError("assistantResult", data.error);
        return;
    }

    document.getElementById("assistantResult").innerHTML = `
        <div class="card">
            <h3>🧠 OpenAI Enterprise Advisor</h3>

            <div class="result">
                <b>Domanda:</b>
                <p>${question}</p>
            </div>

            <div class="result">
                <b>Risposta AI Enterprise:</b>
                <pre style="white-space:pre-wrap;font-family:inherit;">${safeValue(data.answer)}</pre>
            </div>
        </div>
    `;
}

async function loadAssistantMemory() {
    const companyId = getCompanyId();
    const data = await apiGet(`/api/oracle-memory/${companyId}`);

    if (data.error) {
        showError("assistantResult", data.error);
        return;
    }

    const memories = safeArray(data);

    document.getElementById("assistantResult").innerHTML = `
        <div class="card">
            <h3>🧠 Oracle Memory AI</h3>
            ${
                memories.length > 0
                    ? memories.map(m => {
                        const score = safeNumber(m.oracle_score);
                        return `
                            <div class="result">
                                <span class="badge badge-blue">Memoria #${safeValue(m.id)}</span>
                                <span class="badge ${score >= 65 ? "badge-green" : score >= 45 ? "badge-blue" : score >= 25 ? "badge-yellow" : "badge-red"}">
                                    Score ${score}
                                </span>
                                <br><br>
                                <b>Domanda:</b>
                                <p>${safeValue(m.question)}</p>
                                <b>Risposta:</b>
                                <pre style="white-space:pre-wrap;font-family:inherit;">${safeValue(m.answer)}</pre>
                                <small>${safeValue(m.created_at)}</small>
                            </div>
                        `;
                    }).join("")
                    : "<p>Nessuna memoria AI salvata.</p>"
            }
        </div>
    `;
}

async function loadOpenAIUsage() {
    const companyId = getCompanyId();

    const data = await apiGet(`/api/openai/usage/${companyId}`);

    if (data.error) {
        showError("assistantResult", data.error);
        return;
    }

    const logs = safeArray(data);

    document.getElementById("assistantResult").innerHTML = `
        <div class="card">
            <h3>🧠 Storico OpenAI Enterprise</h3>

            ${
                logs.length > 0
                    ? logs.map(log => `
                        <div class="result">
                            <span class="badge badge-blue">${safeValue(log.model)}</span>
                            <br><br>

                            <b>Domanda:</b>
                            <p>${safeValue(log.question)}</p>

                            <b>Risposta:</b>
                            <pre style="white-space:pre-wrap;font-family:inherit;">${safeValue(log.answer)}</pre>

                            <small>${safeValue(log.created_at)}</small>
                        </div>
                    `).join("")
                    : "<p>Nessuna richiesta OpenAI ancora salvata.</p>"
            }
        </div>
    `;
}