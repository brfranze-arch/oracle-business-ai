function renderCyber() {
    setPageTitle("Cyber Oracle AI");

    setContent(`
        <div class="card">
            <h2>🛡 Cyber Oracle AI</h2>
            <p>Gestione asset, finding, minacce, prediction e rischio cyber aziendale.</p>

            <div class="grid-2">
                <div>
                    <h3>🌐 Asset Cyber</h3>
                    <input id="assetType" placeholder="Tipo: domain, subdomain, ip, cloud">
                    <input id="assetValue" placeholder="Valore: azienda.it">
                    <input id="assetProvider" placeholder="Provider: Cloudflare, AWS, Azure, unknown">
                    <textarea id="assetTech" placeholder="Technology stack"></textarea>
                    <textarea id="assetNotes" placeholder="Note"></textarea>
                    <button onclick="createCyberAsset()">Aggiungi Asset</button>
                </div>

                <div>
                    <h3>🛡 Analisi Cyber</h3>
                    <button onclick="loadCyberData()">Carica dati Cyber</button>
                    <button onclick="runCyberAI()">Esegui Cyber Oracle AI</button>
                    <button onclick="loadCyberPredictions()">Carica Predictions</button>
                    <button onclick="loadCyberTimeline()">Cyber Timeline</button>
                </div>
            </div>

            <hr>

            <div class="grid-2">
                <div>
                    <h3>⚠️ Finding</h3>
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
                    <h3>🚨 Threat</h3>
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

    if (data.error) {
        showError("cyberResult", data.error);
        return;
    }

    document.getElementById("cyberResult").innerHTML = `
        <div class="result">
            Asset creato.<br>
            ID: <b>${safeValue(data.id)}</b><br>
            Tipo: ${safeValue(data.asset_type)}<br>
            Valore: ${safeValue(data.value)}<br>
            Provider: ${safeValue(data.provider)}
        </div>
    `;
}

async function loadCyberData() {
    const companyId = getCompanyId();

    const assets = await apiGet(`/api/cyber-assets/${companyId}`);
    const findings = await apiGet(`/api/cyber-findings/${companyId}`);
    const threats = await apiGet(`/api/cyber-threats/${companyId}`);

    if (assets.error || findings.error || threats.error) {
        showError("cyberResult", assets.error || findings.error || threats.error);
        return;
    }

    const assetList = safeArray(assets);
    const findingList = safeArray(findings);
    const threatList = safeArray(threats);

    document.getElementById("cyberResult").innerHTML = `
        <div class="card">
            <h3>🌐 Assets</h3>
            ${
                assetList.length > 0
                    ? assetList.map(a => `
                        <div class="result">
                            <span class="badge badge-blue">ID ${safeValue(a.id)}</span>
                            <b>${safeValue(a.value)}</b><br>
                            Tipo: ${safeValue(a.asset_type)}<br>
                            Provider: ${safeValue(a.provider)}<br>
                            Stack: ${safeValue(a.technology_stack)}<br>
                            Note: ${safeValue(a.notes)}
                        </div>
                    `).join("")
                    : "<p>Nessun asset cyber presente.</p>"
            }

            <h3>⚠️ Findings</h3>
            ${
                findingList.length > 0
                    ? findingList.map(f => `
                        <div class="result">
                            <span class="badge ${severityBadge(f.severity)}">${safeValue(f.severity)}</span>
                            <b>${safeValue(f.title)}</b><br>
                            Categoria: ${safeValue(f.category)}<br>
                            Descrizione: ${safeValue(f.description)}<br>
                            Raccomandazione: ${safeValue(f.recommendation)}
                        </div>
                    `).join("")
                    : "<p>Nessun finding cyber presente.</p>"
            }

            <h3>🚨 Threats</h3>
            ${
                threatList.length > 0
                    ? threatList.map(t => `
                        <div class="result">
                            <span class="badge ${severityBadge(t.severity)}">${safeValue(t.severity)}</span>
                            <b>${safeValue(t.title)}</b><br>
                            Fonte: ${safeValue(t.source)}<br>
                            Tipo: ${safeValue(t.threat_type)}<br>
                            CVE: ${safeValue(t.cve_id)}<br>
                            Score: ${safeNumber(t.score)}<br>
                            Descrizione: ${safeValue(t.description)}
                        </div>
                    `).join("")
                    : "<p>Nessuna threat cyber presente.</p>"
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

    if (data.error) {
        showError("cyberResult", data.error);
        return;
    }

    document.getElementById("cyberResult").innerHTML = `
        <div class="result">
            Finding creato.<br>
            ID: <b>${safeValue(data.id)}</b><br>
            Titolo: ${safeValue(data.title)}<br>
            Severità: <span class="badge ${severityBadge(data.severity)}">${safeValue(data.severity)}</span>
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

    if (data.error) {
        showError("cyberResult", data.error);
        return;
    }

    document.getElementById("cyberResult").innerHTML = `
        <div class="result">
            Threat creata.<br>
            ID: <b>${safeValue(data.id)}</b><br>
            Titolo: ${safeValue(data.title)}<br>
            Severità: <span class="badge ${severityBadge(data.severity)}">${safeValue(data.severity)}</span>
        </div>
    `;
}

async function runCyberAI() {
    const companyId = getCompanyId();
    const data = await apiPost(`/api/cyber-ai/${companyId}`);

    if (data.error) {
        showError("cyberResult", data.error);
        return;
    }

    const cyberScore = safeNumber(data.cyber_score);
    const exposureScore = safeNumber(data.exposure_score);
    const vulnerabilityScore = safeNumber(data.vulnerability_score);
    const threatScore = safeNumber(data.threat_score);
    const predictionScore = safeNumber(data.prediction_score);
    const level = safeValue(data.level, "STABILE");
    const attack30 = safeNumber(data.attack_probability_30d);
    const attack90 = safeNumber(data.attack_probability_90d);

    document.getElementById("cyberResult").innerHTML = `
        <div class="card">
            <h3>🛡 Cyber Oracle AI</h3>

            <span class="badge ${badgeClass(level)}">${level}</span>

            <div class="kpi-value">${cyberScore}/100</div>
            ${progressBar(cyberScore)}

            <div class="kpi-grid">
                <div class="kpi"><div class="kpi-title">Exposure</div><div class="kpi-value">${exposureScore}</div></div>
                <div class="kpi"><div class="kpi-title">Vulnerability</div><div class="kpi-value">${vulnerabilityScore}</div></div>
                <div class="kpi"><div class="kpi-title">Threat</div><div class="kpi-value">${threatScore}</div></div>
                <div class="kpi"><div class="kpi-title">Prediction</div><div class="kpi-value">${predictionScore}</div></div>
            </div>

            <div class="result">
                <h3>🎯 Probabilità attacco</h3>
                <span class="badge badge-yellow">30 giorni: ${attack30}%</span>
                <span class="badge badge-red">90 giorni: ${attack90}%</span>
            </div>

            <div class="result">
                <h3>⚠️ Rischio principale</h3>
                <p>${safeValue(data.main_risk, "Nessun rischio principale rilevato.")}</p>
            </div>

            <div class="result">
                <h3>🤖 Raccomandazione</h3>
                <p>${safeValue(data.recommendation, "Continuare il monitoraggio.")}</p>
            </div>
        </div>
    `;
}

async function loadCyberPredictions() {
    const companyId = getCompanyId();
    const data = await apiGet(`/api/cyber-predictions/${companyId}`);

    if (data.error) {
        showError("cyberResult", data.error);
        return;
    }

    const predictions = safeArray(data);

    document.getElementById("cyberResult").innerHTML = `
        <div class="card">
            <h3>Cyber Predictions salvate</h3>
            ${
                predictions.length > 0
                    ? predictions.map(p => `
                        <div class="result">
                            <span class="badge ${badgeClass(p.level)}">${safeValue(p.level)}</span>
                            <b>Cyber Score: ${safeNumber(p.cyber_score)}/100</b><br>
                            30 giorni: ${safeNumber(p.attack_probability_30d)}%<br>
                            90 giorni: ${safeNumber(p.attack_probability_90d)}%<br>
                            Trend: ${safeValue(p.trend)}<br>
                            Rischio: ${safeValue(p.main_risk)}<br>
                            Raccomandazione: ${safeValue(p.recommendation)}
                        </div>
                    `).join("")
                    : "<p>Nessuna prediction cyber presente.</p>"
            }
        </div>
    `;
}

async function loadCyberTimeline() {
    const companyId = getCompanyId();
    const data = await apiGet(`/api/cyber-timeline/${companyId}`);

    if (data.error) {
        showError("cyberResult", data.error);
        return;
    }

    const timeline = safeArray(data);

    document.getElementById("cyberResult").innerHTML = `
        <div class="card">
            <h3>📈 Cyber Timeline</h3>
            ${
                timeline.length > 0
                    ? timeline.map((s, index) => `
                        <div class="result">
                            <span class="badge badge-blue">Snapshot #${index + 1}</span>
                            <b>Cyber Score: ${safeNumber(s.cyber_score)}/100</b>
                            ${progressBar(safeNumber(s.cyber_score))}
                            Exposure: ${safeNumber(s.exposure_score)}<br>
                            Vulnerability: ${safeNumber(s.vulnerability_score)}<br>
                            Threat: ${safeNumber(s.threat_score)}<br>
                            Prediction: ${safeNumber(s.prediction_score)}<br>
                            Data: ${safeValue(s.created_at)}
                        </div>
                    `).join("")
                    : "<p>Nessuna timeline cyber disponibile.</p>"
            }
        </div>
    `;
}