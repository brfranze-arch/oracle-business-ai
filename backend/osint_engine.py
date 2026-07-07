import socket
import ssl
import urllib.request
from datetime import datetime


def analyze_domain_osint(domain: str):
    findings = []
    score = 100

    dns_status = "ok"
    ssl_status = "unknown"
    http_status = "unknown"

    try:
        socket.gethostbyname(domain)
    except Exception:
        dns_status = "failed"
        score -= 30
        findings.append({
            "title": "DNS non risolvibile",
            "category": "dns",
            "severity": "high",
            "description": f"Il dominio {domain} non risulta risolvibile.",
            "recommendation": "Verificare configurazione DNS, record A/AAAA e provider dominio."
        })

    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                ssl_status = "ok"

                not_after = cert.get("notAfter")
                if not_after:
                    expiry = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                    days_left = (expiry - datetime.utcnow()).days

                    if days_left < 30:
                        score -= 15
                        findings.append({
                            "title": "Certificato SSL in scadenza",
                            "category": "ssl",
                            "severity": "medium",
                            "description": f"Il certificato SSL scade tra {days_left} giorni.",
                            "recommendation": "Rinnovare il certificato SSL prima della scadenza."
                        })

    except Exception:
        ssl_status = "failed"
        score -= 25
        findings.append({
            "title": "SSL non valido o non raggiungibile",
            "category": "ssl",
            "severity": "high",
            "description": "Non è stato possibile verificare correttamente SSL/TLS.",
            "recommendation": "Verificare certificato, porta 443 e configurazione HTTPS."
        })

    try:
        req = urllib.request.Request(
            f"https://{domain}",
            headers={"User-Agent": "OracleBusinessAI-OSINT"}
        )

        with urllib.request.urlopen(req, timeout=5) as response:
            http_status = str(response.status)
            headers = dict(response.headers)

            security_headers = [
                "Strict-Transport-Security",
                "Content-Security-Policy",
                "X-Frame-Options",
                "X-Content-Type-Options"
            ]

            missing = [h for h in security_headers if h not in headers]

            if missing:
                score -= len(missing) * 5
                findings.append({
                    "title": "Security headers mancanti",
                    "category": "headers",
                    "severity": "medium",
                    "description": "Header mancanti: " + ", ".join(missing),
                    "recommendation": "Configurare gli header di sicurezza sul web server o CDN."
                })

    except Exception:
        http_status = "failed"
        score -= 10
        findings.append({
            "title": "Sito HTTPS non raggiungibile",
            "category": "http",
            "severity": "medium",
            "description": "Il sito non è stato raggiunto correttamente via HTTPS.",
            "recommendation": "Verificare hosting, firewall, certificato e redirect HTTPS."
        })

    score = max(0, min(100, score))

    summary = (
        f"OSINT scan completato per {domain}. "
        f"DNS: {dns_status}, SSL: {ssl_status}, HTTP: {http_status}. "
        f"Exposure Score: {score}/100."
    )

    return {
        "domain": domain,
        "dns_status": dns_status,
        "ssl_status": ssl_status,
        "http_status": http_status,
        "exposure_score": score,
        "summary": summary,
        "findings": findings
    }