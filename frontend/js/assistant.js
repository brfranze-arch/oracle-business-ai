function renderAssistant() {
    setPageTitle("Oracle Assistant AI");

    setContent(`
        <div class="card">
            <h2>🤖 Oracle Assistant AI</h2>
            <p>Fai domande all'assistente AI usando i dati reali dell'azienda.</p>

            <textarea id="assistantQuestion" placeholder="Esempio: Come sta andando la mia azienda? Qual è il rischio principale? Quanto ho incassato? Qual è il mio rischio cyber?"></textarea>

            <button onclick="askAssistant()">Chiedi a Oracle Assistant</button>
            <button onclick="loadAssistantMemory()">Carica memoria AI</button>

            <div id="assistantResult"></div>
        </div>
    `);
}

async function askAssistant() {
    const companyId = getCompanyId();
    const question = document.getElementById("assistantQuestion").value;

    if (!question) {
        document.getElementById("assistantResult").innerHTML =
            `<div class="result">Scrivi una domanda.</div>`;
        return;
    }

    const params = new URLSearchParams({
        question: question
    });

    const res = await fetch(`${API}/api/oracle-assistant/${companyId}?${params}`, {
        method: "POST",
        headers: authHeaders()
    });

    const data = await res.json();

    if (data.error) {
        document.getElementById("assistantResult").innerHTML =
            `<div class="result">${data.error}</div>`;
        return;
    }

    document.getElementById("assistantResult").innerHTML = `
        <div class="card">
            <h3>Risposta Oracle Assistant</h3>

            <div class="result">
                <b>Domanda:</b>
                <p>${data.question}</p>
            </div>

            <div class="result">
                <b>Risposta:</b>
                <pre style="white-space:pre-wrap;font-family:inherit;">${data.answer}</pre>
            </div>

            <div class="result">
                <h3>Oracle Score collegato</h3>
                <span class="badge ${badgeClass(data.oracle_score.level)}">${data.oracle_score.level}</span>
                <div class="kpi-value">${data.oracle_score.oracle_score}/100</div>
                ${progressBar(data.oracle_score.oracle_score)}
            </div>
        </div>
    `;
}

async function loadAssistantMemory() {
    const companyId = getCompanyId();

    const data = await apiGet(`/api/oracle-memory/${companyId}`);

    if (!Array.isArray(data)) {
        document.getElementById("assistantResult").innerHTML =
            `<div class="result">${data.error || "Errore caricamento memoria AI"}</div>`;
        return;
    }

    document.getElementById("assistantResult").innerHTML = `
        <div class="card">
            <h3>🧠 Oracle Memory AI</h3>
            ${
                data.length > 0
                    ? data.map(m => `
                        <div class="result">
                            <span class="badge badge-blue">Memoria #${m.id}</span>
                            <span class="badge ${m.oracle_score >= 65 ? "badge-green" : m.oracle_score >= 45 ? "badge-blue" : m.oracle_score >= 25 ? "badge-yellow" : "badge-red"}">
                                Score ${m.oracle_score}
                            </span>
                            <br><br>
                            <b>Domanda:</b>
                            <p>${m.question}</p>
                            <b>Risposta:</b>
                            <pre style="white-space:pre-wrap;font-family:inherit;">${m.answer}</pre>
                            <small>${m.created_at}</small>
                        </div>
                    `).join("")
                    : "<p>Nessuna memoria AI salvata.</p>"
            }
        </div>
    `;
}