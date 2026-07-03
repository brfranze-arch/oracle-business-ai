async function loadTenantSelector() {
    const data = await apiGet("/api/tenants");

    if (data.error) {
        console.log("Tenant error:", data.error);
        return;
    }

    const tenants = safeArray(data);
    const box = document.getElementById("tenantSelectorBox");

    if (!box) return;

    box.innerHTML = `
        <select id="tenantSelector" onchange="selectTenantFromTopbar()">
            ${tenants.map(t => `
                <option value="${t.id}">
                    ${safeValue(t.name)}
                </option>
            `).join("")}
        </select>
    `;

    if (tenants.length > 0) {
        localStorage.setItem("oracle_tenant_id", tenants[0].id);
    }
}

function selectTenantFromTopbar() {
    const id = document.getElementById("tenantSelector").value;
    localStorage.setItem("oracle_tenant_id", id);
}

function getTenantId() {
    return localStorage.getItem("oracle_tenant_id") || "";
}