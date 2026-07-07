def run_finance_agent(revenues):
    total = sum(r.amount for r in revenues)

    if len(revenues) == 0:
        return {
            "summary": "Il Finance Agent non rileva entrate registrate.",
            "actions": "Inserire dati reali di fatturato e monitorare il cash flow.",
            "priority": "high"
        }

    return {
        "summary": f"Il Finance Agent rileva €{round(total, 2)} su {len(revenues)} operazioni.",
        "actions": "Continuare il monitoraggio delle entrate e categorizzare correttamente i ricavi.",
        "priority": "medium"
    }


def run_customer_agent(customers):
    if len(customers) == 0:
        return {
            "summary": "Il Customer Agent non rileva clienti registrati.",
            "actions": "Inserire clienti reali e monitorare la concentrazione del fatturato.",
            "priority": "high"
        }

    return {
        "summary": f"Il Customer Agent rileva {len(customers)} clienti registrati.",
        "actions": "Analizzare il valore dei clienti principali e ridurre la dipendenza da pochi clienti.",
        "priority": "medium"
    }


def run_compliance_agent(items):
    pending = [i for i in items if i.status != "completato"]

    if len(items) == 0:
        return {
            "summary": "Il Compliance Agent non rileva elementi compliance.",
            "actions": "Inserire GDPR, licenze, assicurazioni, scadenze e documenti obbligatori.",
            "priority": "high"
        }

    if pending:
        return {
            "summary": f"Il Compliance Agent rileva {len(pending)} elementi pendenti.",
            "actions": "Completare gli elementi compliance pendenti o scaduti.",
            "priority": "high"
        }

    return {
        "summary": "Il Compliance Agent non rileva criticità immediate.",
        "actions": "Continuare il monitoraggio delle scadenze.",
        "priority": "low"
    }


def run_cyber_agent(findings, threats):
    critical = [
        f for f in findings
        if str(f.severity).lower() in ["high", "critical"]
    ]

    if critical or threats:
        return {
            "summary": f"Il Cyber Agent rileva {len(critical)} finding critici e {len(threats)} threat.",
            "actions": "Intervenire sui finding ad alta severità e monitorare le minacce.",
            "priority": "high"
        }

    return {
        "summary": "Il Cyber Agent non rileva minacce critiche immediate.",
        "actions": "Continuare scansioni OSINT, Cyber AI e aggiornamenti periodici.",
        "priority": "medium"
    }


def run_executive_agent(agent_results):
    high = [r for r in agent_results if r["priority"] == "high"]

    if high:
        return {
            "summary": f"Executive Agent: rilevate {len(high)} aree ad alta priorità.",
            "actions": "Concentrarsi prima sulle criticità Finance, Compliance, Cyber o Customer segnalate.",
            "priority": "high"
        }

    return {
        "summary": "Executive Agent: situazione complessivamente sotto controllo.",
        "actions": "Continuare il monitoraggio e aggiornare i dati aziendali.",
        "priority": "medium"
    }