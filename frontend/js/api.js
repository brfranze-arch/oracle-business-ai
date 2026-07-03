const API = "https://oracle-business-ai-backend.onrender.com";

function token() {
    return localStorage.getItem("oracle_token");
}

function authHeaders() {

    return {

        "Authorization":
            "Bearer " + localStorage.getItem("oracle_token"),

        "X-Tenant-Id":
            getTenantId()

    };

}

async function apiGet(url) {
    try {
        const res = await fetch(API + url, {
            headers: authHeaders()
        });

        return await res.json();
    } catch (e) {
        return {
            error: "Errore di connessione al backend."
        };
    }
}

async function apiPost(url, body = null) {
    try {
        const options = {
            method: "POST",
            headers: authHeaders()
        };

        if (body) {
            options.headers["Content-Type"] = "application/json";
            options.body = JSON.stringify(body);
        }

        const res = await fetch(API + url, options);
        return await res.json();
    } catch (e) {
        return {
            error: "Errore di connessione al backend."
        };
    }
}