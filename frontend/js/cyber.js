function renderCyber() {
    setPageTitle("Cyber Oracle AI");

    setContent(`
        <div class="card">
            <h2>🛡 Cyber Oracle AI</h2>
            <p>Gestione asset cyber, finding, minacce, score e predizione rischio.</p>

            <div class="grid-2">
                <div>
                    <h3>🌐 Aggiungi Asset Cyber</h3>
                    <input id="assetType" placeholder="Tipo: domain, subdomain, ip, cloud">
                    <input id="assetValue" placeholder="Valore: azienda.it, api.azienda.it">
                    <input id="assetProvider" placeholder="Provider: Cloudflare, AWS, Azure, unknown">
                    <textarea id="assetTech" placeholder="Technology stack"></textarea>
                    <textarea id="assetNotes" placeholder="Note"></textarea>
                    <button onclick="createCyberAsset()">Aggiungi Asset</button>
                </div>

                <div>
                    <h3>🛡 Analisi Cyber</h3>
                    <button onclick="loadCyberAssets()">Carica Assets</button>
                    <button onclick="runCyberAI()">Esegui Cyber Oracle AI</button>
                    <button onclick="loadCyberPredictions()">Carica Predictions</button>
                    <button onclick="loadCyberTimeline()">Cyber Timeline</button>
                </div>
            </div>

            <hr>

            <div class="grid-2">
                <div>
                    <h3>⚠️ Aggiungi Finding</h3>
                    <input id="findingAssetId" placeholder="ID asset">
                    <input id="findingTitle" placeholder="Titolo finding">
                    <input id="findingCategory" placeholder="Categoria: ssl, dns, headers, cve">
                    <select id="findingSeverity">
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                        <option value="critical">Critical</option>
                    </select>
                    <textarea id="findingDescription" placeholder="Descrizione"></textarea>
                    <textarea id="findingRecommendation" placeholder="Raccomandazione"></textarea>
                    <button onclick="createCyberFinding()">Aggiungi Finding</button>
                </div>

                <div>
                    <h3>🚨 Aggiungi Threat</h3>
                    <input id="threatSource" placeholder="Fonte: NVD, CISA KEV, OSINT">
                    <input id="threatType" placeholder="Tipo: cve, ransomware, phishing">
                    <input id="threatTitle" placeholder="Titolo threat">
                    <input id="threatCve" placeholder="CVE opzionale">
                    <select id="threatSeverity">
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                        <option value="critical">Critical</option>
                    </select>
                    <input id="threatScore" type="number" placeholder="Score 0-100">
                    <textarea id="threatDescription" placeholder="Descrizione"></textarea>
                    <button onclick="createCyberThreat()">Aggiungi Threat</button>
                </div>
            </div>

            <div id="cyberResult"></div>
        </div>
    `);
}

function severityBadge(severity) {
    const s = (severity || "").toLowerCase();

    if (s === "critical") return "badge-red";
    if (s === "high") return "badge-red";
    if (s === "medium") return "badge-yellow";
    if (s === "low") return "badge-blue";

    return "badge-blue";
}

async function createCyberAsset() {
    const companyId = getCompanyId();

    const params = new URLSearchParams({
        company_id: companyId,
        asset_type: document.getElementById("assetType").value,
        value: document.getElementById("assetValue").value,
        provider: document.getElementById("assetProvider").value || "unknown",
        technology_stack: document.getElementById("assetTech").value,
        notes: document.getElementById("assetNotes").value
    });

    const res = await fetch(`${API}/api/cyber-assets?${params}`, {
        method: "POST",
        headers: authHeaders()
    });

    const data = await res.json();

    document.getElementById("cyberResult").innerHTML = `
        <div class="result">
            Asset creato.<br>
            ID: <b>${data.id}</b><br>
            Tipo: ${data.asset_type}<br>
            Valore: ${data.value}<br>
            Provider: ${data.provider}
        </div>
    `;
}

async function loadCyberAssets() {
    const companyId = getCompanyId();

    const assets = await apiGet(`/api/cyber-assets/${companyId}`);
    const findings = await apiGet(`/api/cyber-findings/${companyId}`);
    const threats = await apiGet(`/api/cyber-threats/${companyId}`);

    document.getElementById("cyberResult").innerHTML = `
        <div class="card">
            <h3>🌐 Cyber Assets</h3>
            ${
                Array.isArray(assets) && assets.length > 0
                    ? assets.map(a => `
                        <div class="result">
                            <span class="badge badge-blue">ID ${a.id}</span>
                            <b>${a.value}</b><br>
                            Tipo: ${a.asset_type}<br>
                            Provider: ${a.provider}<br>
                            Stack: ${a.technology_stack || "-"}<br>
                            Note: ${a.notes || "-"}
                        </div>
                    `).join("")
                    : "<p>Nessun asset cyber.</p>"
            }

            <h3>⚠️ Findings</h3>
            ${
                Array.isArray(findings) && findings.length > 0
                    ? findings.map(f => `
                        <div class="result">
                            <span class="badge ${severityBadge(f.severity)}">${f.severity}</span>
                            <b>${f.title}</b><br>
                            Categoria: ${f.category}<br>
                            Descrizione: ${f.description}<br>
                            Raccomandazione: ${f.recommendation}
                        </div>
                    `).join("")
                    : "<p>Nessun finding cyber.</p>"
            }

            <h3>🚨 Threats</h3>
            ${
                Array.isArray(threats) && threats.length > 0
                    ? threats.map(t => `
                        <div class="result">
                            <span class="badge ${severityBadge(t.severity)}">${t.severity}</span>
                            <b>${t.title}</b><br>
                            Fonte: ${t.source}<br>
                            Tipo: ${t.threat_type}<br>
                            CVE: ${t.cve_id || "-"}<br>
                            Score: ${t.score}<br>
                            Descrizione: ${t.description}
                        </div>
                    `).join("")
                    : "<p>Nessuna threat cyber.</p>"
            }
        </div>
    `;
}

async function createCyberFinding() {
    const companyId = getCompanyId();

    const params = new URLSearchParams({
        company_id: companyId,
        asset_id: document.getElementById("findingAssetId").value,
        title: document.getElementById("findingTitle").value,
        category: document.getElementById("findingCategory").value,
        severity: document.getElementById("findingSeverity").value,
        description: document.getElementById("findingDescription").value,
        recommendation: document.getElementById("findingRecommendation").value,
        scan_id: 0
    });

    const res = await fetch(`${API}/api/cyber-findings?${params}`, {
        method: "POST",
        headers: authHeaders()
    });

    const data = await res.json();

    document.getElementById("cyberResult").innerHTML = `
        <div class="result">
            Finding creato.<br>
            ID: <b>${data.id}</b><br>
            Titolo: ${data.title}<br>
            Severità: <span class="badge ${severityBadge(data.severity)}">${data.severity}</span>
        </div>
    `;
}

async function createCyberThreat() {
    const companyId = getCompanyId();

    const params = new URLSearchParams({
        company_id: companyId,
        source: document.getElementById("threatSource").value,
        threat_type: document.getElementById("threatType").value,
        title: document.getElementById("threatTitle").value,
        description: document.getElementById("threatDescription").value,
        severity: document.getElementById("threatSeverity").value,
        score: document.getElementById("threatScore").value || 50,
        cve_id: document.getElementById("threatCve").value
    });

    const res = await fetch(`${API}/api/cyber-threats?${params}`, {
        method: "POST",
        headers: authHeaders()
    });

    const data = await res.json();

    document.getElementById("cyberResult").innerHTML = `
        <div class="result">
            Threat creata.<br>
            ID: <b>${data.id}</b><br>
            Titolo: ${data.title}<br>
            Severità: <span class="badge ${severityBadge(data.severity)}">${data.severity}</span>
        </div>
    `;
}

async function runCyberAI() {
    const companyId = getCompanyId();

    const data = await apiPost(`/api/cyber-ai/${companyId}`);

    if (data.error) {
        document.getElementById("cyberResult").innerHTML =
            `<div class="result">${data.error}</div>`;
        return;
    }

    document.getElementById("cyberResult").innerHTML = `
        <div class="card">
            <h3>🛡 Cyber Oracle AI</h3>

            <span class="badge ${badgeClass(data.level)}">${data.level}</span>

            <div class="kpi-value">${data.cyber_score}/100</div>
            ${progressBar(data.cyber_score)}

            <div class="kpi-grid">
                <div class="kpi">
                    <div class="kpi-title">Exposure</div>
                    <div class="kpi-value">${data.exposure_score}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Vulnerability</div>
                    <div class="kpi-value">${data.vulnerability_score}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Threat</div>
                    <div class="kpi-value">${data.threat_score}</div>
                </div>

                <div class="kpi">
                    <div class="kpi-title">Prediction</div>
                    <div class="kpi-value">${data.prediction_score}</div>
                </div>
            </div>

            <div class="result">
                <h3>🎯 Probabilità attacco</h3>
                <span class="badge badge-yellow">30 giorni: ${data.attack_probability_30d}%</span>
                <span class="badge badge-red">90 giorni: ${data.attack_probability_90d}%</span>
            </div>

            <div class="result">
                <h3>⚠️ Rischio principale</h3>
                <p>${data.main_risk}</p>
            </div>

            <div class="result">
                <h3>🤖 Raccomandazione</h3>
                <p>${data.recommendation}</p>
            </div>
        </div>
    `;
}

async function loadCyberPredictions() {
    const companyId = getCompanyId();
    const data = await apiGet(`/api/cyber-predictions/${companyId}`);

    if (!Array.isArray(data)) {
        document.getElementById("cyberResult").innerHTML =
            `<div class="result">${data.error || "Errore caricamento predictions"}</div>`;
        return;
    }

    document.getElementById("cyberResult").innerHTML = `
        <div class="card">
            <h3>Cyber Predictions salvate</h3>
            ${
                data.length > 0
                    ? data.map(p => `
                        <div class="result">
                            <span class="badge ${badgeClass(p.level)}">${p.level}</span>
                            <b>Cyber Score: ${p.cyber_score}/100</b><br>
                            30 giorni: ${p.attack_probability_30d}%<br>
                            90 giorni: ${p.attack_probability_90d}%<br>
                            Trend: ${p.trend}<br>
                            Rischio: ${p.main_risk}<br>
                            Raccomandazione: ${p.recommendation}
                        </div>
                    `).join("")
                    : "<p>Nessuna prediction cyber.</p>"
            }
        </div>
    `;
}

async function loadCyberTimeline() {
    const companyId = getCompanyId();
    const data = await apiGet(`/api/cyber-timeline/${companyId}`);

    if (!Array.isArray(data)) {
        document.getElementById("cyberResult").innerHTML =
            `<div class="result">${data.error || "Errore timeline cyber"}</div>`;
        return;
    }

    document.getElementById("cyberResult").innerHTML = `
        <div class="card">
            <h3>📈 Cyber Timeline</h3>
            ${
                data.length > 0
                    ? data.map((s, index) => `
                        <div class="result">
                            <span class="badge badge-blue">Snapshot #${index + 1}</span>
                            <b>Cyber Score: ${s.cyber_score}/100</b>
                            ${progressBar(s.cyber_score)}
                            Exposure: ${s.exposure_score}<br>
                            Vulnerability: ${s.vulnerability_score}<br>
                            Threat: ${s.threat_score}<br>
                            Prediction: ${s.prediction_score}<br>
                            Data: ${s.created_at}
                        </div>
                    `).join("")
                    : "<p>Nessuna timeline cyber ancora presente.</p>"
            }
        </div>
    `;
}