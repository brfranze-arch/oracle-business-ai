def analyze_finance(company, revenues):
    total = sum(r.amount for r in revenues)

    cash = sum(r.amount for r in revenues if r.payment_method == "contanti")
    pos = sum(r.amount for r in revenues if r.payment_method == "pos")
    bank = sum(r.amount for r in revenues if r.payment_method == "bonifico")
    digital = sum(r.amount for r in revenues if r.payment_method == "digitale")

    score = 50
    messages = []

    if total <= 0:
        return {
            "title": "Nessuna entrata registrata",
            "message": "Non ci sono ancora dati sufficienti.",
            "score": 0,
            "level": "BASSO"
        }

    cash_percent = (cash / total) * 100

    if cash_percent > 60:
        score -= 20
        messages.append("Elevata dipendenza dal contante.")

    if pos + digital + bank > cash:
        score += 20
        messages.append("Buona presenza di pagamenti tracciabili.")

    if total > 5000:
        score += 15
        messages.append("Volume entrate interessante.")

    if not messages:
        messages.append("Situazione finanziaria stabile, servono più dati per previsioni avanzate.")

    if score >= 75:
        level = "OTTIMO"
    elif score >= 55:
        level = "BUONO"
    elif score >= 35:
        level = "ATTENZIONE"
    else:
        level = "CRITICO"

    return {
        "title": "Analisi AI Entrate",
        "message": " ".join(messages),
        "score": score,
        "level": level
    }

def calculate_oracle_score(company, revenues, insights, health_reports=None, customer_insights=None, compliance_insights=None, cyber_predictions=None):
    if health_reports is None:
        health_reports = []

    if customer_insights is None:
        customer_insights = []

    if compliance_insights is None:
        compliance_insights = []

    if cyber_predictions is None:
        cyber_predictions = []

    if health_reports is None:
        health_reports = []

    total_revenue = sum(r.amount for r in revenues)
    total_operations = len(revenues)

    cash = sum(r.amount for r in revenues if r.payment_method == "contanti")
    traced = sum(
        r.amount for r in revenues
        if r.payment_method in ["pos", "bonifico", "digitale"]
    )

    finance_score = 50
    business_health_score = 50

    strengths = []
    risks = []
    suggestions = []

    if total_revenue > 0:
        finance_score += 15
        strengths.append("L'azienda ha entrate reali registrate.")
    else:
        finance_score -= 20
        risks.append("Non sono presenti entrate registrate.")
        suggestions.append("Inserire dati reali di entrata per migliorare l'analisi AI.")

    if total_operations >= 4:
        finance_score += 10
        strengths.append("Sono presenti più operazioni finanziarie.")
    else:
        finance_score -= 5
        risks.append("Numero di operazioni ancora basso.")

    if traced > cash:
        finance_score += 15
        strengths.append("I pagamenti tracciabili superano i contanti.")
    elif cash > traced and total_revenue > 0:
        finance_score -= 15
        risks.append("I contanti superano i pagamenti tracciabili.")
        suggestions.append("Aumentare POS, bonifici o pagamenti digitali.")

    finance_insights = [
        i.score for i in insights
        if i.module == "finance" and i.score is not None
    ]

    if finance_insights:
        avg_finance_ai = sum(finance_insights) / len(finance_insights)
        finance_score = (finance_score + avg_finance_ai) / 2
        strengths.append("Il punteggio include gli insight Finance Oracle AI.")

    if health_reports:
        latest_health = health_reports[0]
        business_health_score = latest_health.health_score
        strengths.append("Il punteggio include anche Business Health AI.")
    else:
        risks.append("Business Health AI non ancora analizzato.")
        suggestions.append("Generare un report Business Health per rendere l'Oracle Score più completo.")

    finance_score = max(0, min(100, finance_score))
    business_health_score = max(0, min(100, business_health_score))

    if cyber_predictions:
        cyber_score = cyber_predictions[0].cyber_score
        strengths.append("Il punteggio include anche Cyber Oracle AI.")
    else:
        cyber_score = 50
        risks.append("Cyber Oracle AI non ancora analizzato.")
        suggestions.append("Generare un report Cyber Oracle AI per valutare dominio, asset e minacce.")

    if compliance_insights:
        compliance_score = compliance_insights[0].compliance_score
        strengths.append("Il punteggio include anche Compliance Oracle AI.")
    else:
        compliance_score = 50
        risks.append("Compliance Oracle AI non ancora analizzato.")
        suggestions.append("Generare un report Compliance Oracle AI per valutare scadenze, GDPR, sicurezza e documenti.")
    if customer_insights:
    	customer_score = customer_insights[0].customer_score
    	strengths.append("Il punteggio include anche Customer Oracle AI.")
    else:
    	customer_score = 50
    	risks.append("Customer Oracle AI non ancora analizzato.")
    	suggestions.append("Generare un report Customer Oracle AI per valutare clienti e concentrazione del fatturato.")

    oracle_score = (
        finance_score * 0.35 +
        business_health_score * 0.25 +
        cyber_score * 0.20 +
        compliance_score * 0.10 +
        customer_score * 0.10
    )

    oracle_score = round(oracle_score, 2)

    if oracle_score >= 80:
        level = "ECCELLENTE"
    elif oracle_score >= 65:
        level = "FORTE"
    elif oracle_score >= 45:
        level = "STABILE"
    elif oracle_score >= 25:
        level = "FRAGILE"
    else:
        level = "CRITICO"

    return {
        "company_id": company.id,
        "company_name": company.name,
        "oracle_score": oracle_score,
        "level": level,
        "finance_score": round(finance_score, 2),
        "business_health_score": round(business_health_score, 2),
        "cyber_score": cyber_score,
        "compliance_score": compliance_score,
        "customer_score": customer_score,
        "total_revenue": total_revenue,
        "total_operations": total_operations,
        "cash": cash,
        "traced_payments": traced,
        "strengths": strengths,
        "risks": risks,
        "suggestions": suggestions
    }

def analyze_business_health(company, revenues, insights):
    total_revenue = sum(r.amount for r in revenues)
    operations_count = len(revenues)

    cash = sum(r.amount for r in revenues if r.payment_method == "contanti")
    traced = sum(
        r.amount for r in revenues
        if r.payment_method in ["pos", "bonifico", "digitale"]
    )

    categories = {}

    for r in revenues:
        if r.category not in categories:
            categories[r.category] = 0
        categories[r.category] += r.amount

    best_category = None
    if categories:
        best_category = max(categories, key=categories.get)

    score = 50

    main_strength = "L'azienda ha una base dati iniziale utile per l'analisi."
    main_risk = "Servono più dati per rendere la previsione più precisa."
    recommendation = "Continua a registrare entrate e categorie per migliorare l'intelligenza della piattaforma."

    if total_revenue > 0:
        score += 15
        main_strength = f"L'azienda ha registrato entrate reali per €{round(total_revenue, 2)}."

    if operations_count >= 5:
        score += 10
        main_strength += " Il numero di operazioni è sufficiente per una prima valutazione."
    elif operations_count < 3:
        score -= 10
        main_risk = "Il numero di operazioni registrate è ancora basso."

    if traced > cash:
        score += 15
    elif cash > traced and total_revenue > 0:
        score -= 15
        main_risk = "I pagamenti in contanti superano quelli tracciabili."
        recommendation = "Aumenta POS, bonifici o pagamenti digitali per migliorare controllo e previsione."

    if best_category:
        main_strength += f" La categoria più forte è: {best_category}."

    finance_scores = [
        i.score for i in insights
        if i.module == "finance" and i.score is not None
    ]

    if finance_scores:
        avg_finance = sum(finance_scores) / len(finance_scores)
        score = (score + avg_finance) / 2

    if score > 100:
        score = 100

    if score < 0:
        score = 0

    score = round(score, 2)

    if score >= 80:
        level = "ECCELLENTE"
    elif score >= 65:
        level = "FORTE"
    elif score >= 45:
        level = "STABILE"
    elif score >= 25:
        level = "FRAGILE"
    else:
        level = "CRITICO"

    return {
        "health_score": score,
        "level": level,
        "revenue_total": total_revenue,
        "operations_count": operations_count,
        "main_strength": main_strength,
        "main_risk": main_risk,
        "recommendation": recommendation
    }

def analyze_customers(company, customers, revenues):
    score = 50
    customers_count = len(customers)

    message_parts = []
    recommendation_parts = []

    if customers_count == 0:
        return {
            "customer_score": 20,
            "level": "FRAGILE",
            "top_customer_name": "",
            "top_customer_revenue": 0,
            "customers_count": 0,
            "message": "Non sono ancora presenti clienti registrati.",
            "recommendation": "Inserisci clienti reali e collega le entrate ai clienti per ottenere analisi più precise."
        }

    if customers_count >= 3:
        score += 15
        message_parts.append("La base clienti inizia ad avere dati utili.")
    else:
        score -= 5
        message_parts.append("La base clienti è ancora piccola.")

    customer_revenues = {}

    for customer in customers:
        customer_revenues[customer.id] = 0

    for revenue in revenues:
        customer_id = getattr(revenue, "customer_id", None)
        if customer_id in customer_revenues:
            customer_revenues[customer_id] += revenue.amount

    top_customer_id = None
    top_customer_revenue = 0

    for cid, total in customer_revenues.items():
        if total > top_customer_revenue:
            top_customer_id = cid
            top_customer_revenue = total

    top_customer_name = ""

    if top_customer_id:
        for customer in customers:
            if customer.id == top_customer_id:
                top_customer_name = customer.name
                break

    total_revenue = sum(r.amount for r in revenues)

    if total_revenue > 0 and top_customer_revenue > 0:
        concentration = (top_customer_revenue / total_revenue) * 100

        if concentration > 50:
            score -= 10
            message_parts.append("Una parte elevata delle entrate dipende da un solo cliente.")
            recommendation_parts.append("Riduci la dipendenza da un singolo cliente acquisendo nuovi clienti.")
        else:
            score += 10
            message_parts.append("Le entrate risultano distribuite in modo più equilibrato.")

    if top_customer_revenue > 0:
        score += 10
        message_parts.append(f"Il cliente migliore genera €{round(top_customer_revenue, 2)}.")

    score = max(0, min(100, score))

    if score >= 80:
        level = "ECCELLENTE"
    elif score >= 65:
        level = "FORTE"
    elif score >= 45:
        level = "STABILE"
    elif score >= 25:
        level = "FRAGILE"
    else:
        level = "CRITICO"

    if not recommendation_parts:
        recommendation_parts.append("Continua a registrare clienti ed entrate collegate per migliorare le previsioni AI.")

    return {
        "customer_score": round(score, 2),
        "level": level,
        "top_customer_name": top_customer_name,
        "top_customer_revenue": round(top_customer_revenue, 2),
        "customers_count": customers_count,
        "message": " ".join(message_parts),
        "recommendation": " ".join(recommendation_parts)
    }

from datetime import datetime


def analyze_compliance(company, items):
    total_items = len(items)
    completed_items = 0
    pending_items = 0
    expired_items = 0

    today = datetime.utcnow().date()

    for item in items:
        status = (item.status or "").lower()

        if status in ["completato", "ok", "done"]:
            completed_items += 1
        else:
            pending_items += 1

        if item.due_date:
            try:
                due = datetime.strptime(item.due_date, "%Y-%m-%d").date()
                if due < today and status not in ["completato", "ok", "done"]:
                    expired_items += 1
            except Exception:
                pass

    score = 50
    message_parts = []
    recommendation_parts = []

    if total_items == 0:
        return {
            "compliance_score": 20,
            "level": "FRAGILE",
            "total_items": 0,
            "completed_items": 0,
            "pending_items": 0,
            "expired_items": 0,
            "message": "Non sono ancora presenti elementi di compliance.",
            "recommendation": "Inserisci scadenze, documenti, GDPR, sicurezza, licenze o assicurazioni da monitorare."
        }

    completion_rate = (completed_items / total_items) * 100

    if completion_rate >= 70:
        score += 25
        message_parts.append("Buona percentuale di elementi completati.")
    elif completion_rate >= 40:
        score += 5
        message_parts.append("Compliance parzialmente gestita.")
    else:
        score -= 15
        message_parts.append("Molti elementi risultano ancora non completati.")

    if expired_items > 0:
        score -= expired_items * 10
        message_parts.append(f"Sono presenti {expired_items} elementi scaduti.")
        recommendation_parts.append("Gestisci subito gli elementi scaduti per ridurre il rischio operativo e legale.")

    if pending_items > 0:
        recommendation_parts.append("Completa gli elementi pendenti e aggiorna lo stato in piattaforma.")

    score = max(0, min(100, score))

    if score >= 80:
        level = "ECCELLENTE"
    elif score >= 65:
        level = "FORTE"
    elif score >= 45:
        level = "STABILE"
    elif score >= 25:
        level = "FRAGILE"
    else:
        level = "CRITICO"

    return {
        "compliance_score": round(score, 2),
        "level": level,
        "total_items": total_items,
        "completed_items": completed_items,
        "pending_items": pending_items,
        "expired_items": expired_items,
        "message": " ".join(message_parts),
        "recommendation": " ".join(recommendation_parts)
    }

def oracle_assistant_answer(
    company,
    question,
    oracle_score_data,
    revenues,
    customers,
    compliance_insights,
    cyber_predictions=None,
    cyber_findings=None,
    cyber_threats=None,
    cyber_assets=None
):

    if cyber_predictions is None:
        cyber_predictions = []

    if cyber_findings is None:
        cyber_findings = []

    if cyber_threats is None:
        cyber_threats = []

    if cyber_assets is None:
        cyber_assets = []

    q = question.lower()

    total_revenue = oracle_score_data.get("total_revenue", 0)
    cash = oracle_score_data.get("cash", 0)
    traced = oracle_score_data.get("traced_payments", 0)
    total_operations = oracle_score_data.get("total_operations", 0)

    finance_score = oracle_score_data.get("finance_score", 50)
    business_health_score = oracle_score_data.get("business_health_score", 50)
    customer_score = oracle_score_data.get("customer_score", 50)
    compliance_score = oracle_score_data.get("compliance_score", 50)
    cyber_score = oracle_score_data.get("cyber_score", 50)

    oracle_score = oracle_score_data.get("oracle_score", 0)
    oracle_level = oracle_score_data.get("level", "NON DISPONIBILE")

    strengths = oracle_score_data.get("strengths", [])
    risks = oracle_score_data.get("risks", [])
    suggestions = oracle_score_data.get("suggestions", [])

    response_parts = []

    response_parts.append(
        f"Oracle Assistant AI — {company.name}\n"
        f"Oracle Score attuale: {oracle_score}/100, livello {oracle_level}."
    )

    # ANDAMENTO GENERALE
    if any(word in q for word in [
        "come sta andando",
        "andamento",
        "situazione",
        "stato azienda",
        "stato dell'azienda",
        "panoramica",
        "generale",
        "dashboard"
    ]):
        response_parts.append("\nSintesi generale aziendale:")

        response_parts.append(f"- Finance Score: {finance_score}/100")
        response_parts.append(f"- Business Health Score: {business_health_score}/100")
        response_parts.append(f"- Customer Score: {customer_score}/100")
        response_parts.append(f"- Compliance Score: {compliance_score}/100")
        response_parts.append(f"- Cyber Score: {cyber_score}/100")

        if oracle_score >= 80:
            response_parts.append("\nL'azienda appare in una condizione molto forte.")
        elif oracle_score >= 65:
            response_parts.append("\nL'azienda è in una condizione positiva, ma ci sono aree da migliorare.")
        elif oracle_score >= 45:
            response_parts.append("\nL'azienda è stabile, ma servono più dati e interventi mirati.")
        elif oracle_score >= 25:
            response_parts.append("\nL'azienda è fragile: alcune aree richiedono attenzione.")
        else:
            response_parts.append("\nL'azienda è in condizione critica o con dati insufficienti.")

    # ENTRATE / FATTURATO
    elif any(word in q for word in [
        "entrate",
        "incasso",
        "incassato",
        "fatturato",
        "ricavi",
        "vendite",
        "guadagnato",
        "quanto ho fatto",
        "quanto ho incassato"
    ]):
        response_parts.append("\nAnalisi entrate:")

        response_parts.append(f"- Entrate totali registrate: €{total_revenue}")
        response_parts.append(f"- Numero operazioni: {total_operations}")
        response_parts.append(f"- Contanti: €{cash}")
        response_parts.append(f"- Pagamenti tracciabili: €{traced}")

        if total_revenue <= 0:
            response_parts.append("\nNon risultano ancora entrate registrate.")
            response_parts.append("Suggerimento: inserisci entrate reali oppure importa un file CSV/Excel.")
        else:
            if traced > cash:
                response_parts.append("\nLa situazione è positiva: i pagamenti tracciabili superano i contanti.")
            elif cash > traced:
                response_parts.append("\nAttenzione: i contanti superano i pagamenti tracciabili.")
            else:
                response_parts.append("\nContanti e pagamenti tracciabili sono bilanciati.")

    # CONTANTI / TRACCIABILI
    elif any(word in q for word in [
        "contanti",
        "pos",
        "bonifico",
        "digitale",
        "tracciabili",
        "pagamenti",
        "metodi pagamento"
    ]):
        response_parts.append("\nAnalisi metodi di pagamento:")

        response_parts.append(f"- Contanti: €{cash}")
        response_parts.append(f"- Pagamenti tracciabili: €{traced}")

        if total_revenue > 0:
            cash_percent = round((cash / total_revenue) * 100, 2)
            traced_percent = round((traced / total_revenue) * 100, 2)

            response_parts.append(f"- Percentuale contanti: {cash_percent}%")
            response_parts.append(f"- Percentuale tracciabili: {traced_percent}%")

            if cash_percent > 60:
                response_parts.append("\nRischio: alta dipendenza dal contante.")
                response_parts.append("Suggerimento: aumentare POS, bonifici e pagamenti digitali.")
            else:
                response_parts.append("\nLa gestione dei pagamenti è abbastanza sana.")
        else:
            response_parts.append("\nNon ci sono ancora entrate sufficienti per calcolare percentuali.")

    # CLIENTI
    elif any(word in q for word in [
        "cliente",
        "clienti",
        "customer",
        "miglior cliente",
        "cliente migliore",
        "dipendenza cliente",
        "fidelizzazione"
    ]):
        response_parts.append("\nAnalisi clienti:")

        response_parts.append(f"- Clienti registrati: {len(customers)}")
        response_parts.append(f"- Customer Score: {customer_score}/100")

        if len(customers) == 0:
            response_parts.append("\nNon sono ancora presenti clienti registrati.")
            response_parts.append("Suggerimento: inserisci clienti e collega le entrate ai clienti.")
        else:
            response_parts.append("\nLa piattaforma sta già raccogliendo dati utili sui clienti.")
            response_parts.append("Può analizzare concentrazione fatturato, cliente migliore e rischio dipendenza.")

            if customer_score < 45:
                response_parts.append("\nArea critica: il modulo clienti è debole.")
            elif customer_score < 65:
                response_parts.append("\nArea da migliorare: la base clienti può essere rafforzata.")
            else:
                response_parts.append("\nLa base clienti appare discreta o forte.")

    # COMPLIANCE
    elif any(word in q for word in [
        "compliance",
        "gdpr",
        "privacy",
        "scadenze",
        "documenti",
        "licenze",
        "assicurazione",
        "assicurazioni",
        "sicurezza documentale"
    ]):
        response_parts.append("\nAnalisi Compliance:")

        response_parts.append(f"- Compliance Score: {compliance_score}/100")

        if compliance_insights:
            latest = compliance_insights[0]
            response_parts.append(f"- Livello: {latest.level}")
            response_parts.append(f"- Elementi totali: {latest.total_items}")
            response_parts.append(f"- Completati: {latest.completed_items}")
            response_parts.append(f"- Pendenti: {latest.pending_items}")
            response_parts.append(f"- Scaduti: {latest.expired_items}")
            response_parts.append(f"\nAnalisi: {latest.message}")
            response_parts.append(f"Raccomandazione: {latest.recommendation}")
        else:
            response_parts.append("\nNon è ancora stata generata un'analisi Compliance AI.")
            response_parts.append("Suggerimento: inserisci documenti, scadenze, GDPR, licenze e assicurazioni.")

    # RISCHI
    elif any(word in q for word in [
        "rischio",
        "rischi",
        "problema",
        "problemi",
        "criticità",
        "critico",
        "debolezza",
        "cosa non va"
    ]):
        response_parts.append("\nRischi principali rilevati:")

        if risks:
            for r in risks:
                response_parts.append(f"- {r}")
        else:
            response_parts.append("- Nessun rischio importante rilevato al momento.")

        if compliance_score < 45:
            response_parts.append("- Compliance bassa: possibile rischio su documenti, scadenze o GDPR.")

        if customer_score < 45:
            response_parts.append("- Customer Score basso: possibile rischio clienti o fatturato concentrato.")

        if finance_score < 45:
            response_parts.append("- Finance Score basso: dati finanziari insufficienti o situazione debole.")

        if cyber_score == 50:
            response_parts.append("- Cyber Score ancora neutro: il modulo Cyber Oracle AI non è stato completato.")

    # PUNTI FORTI
    elif any(word in q for word in [
        "punti forti",
        "forza",
        "vantaggi",
        "cosa va bene",
        "positivo",
        "migliori aspetti"
    ]):
        response_parts.append("\nPunti forti rilevati:")

        if strengths:
            for s in strengths:
                response_parts.append(f"- {s}")
        else:
            response_parts.append("- Non sono ancora emersi punti forti chiari. Servono più dati.")

        best_module = max(
            [
                ("Finance", finance_score),
                ("Business Health", business_health_score),
                ("Customer", customer_score),
                ("Compliance", compliance_score),
                ("Cyber", cyber_score),
            ],
            key=lambda x: x[1]
        )

        response_parts.append(
            f"\nModulo più forte al momento: {best_module[0]} con score {best_module[1]}/100."
        )

    # SUGGERIMENTI / PRIORITÀ
    elif any(word in q for word in [
        "suggerimenti",
        "consigli",
        "cosa devo fare",
        "priorità",
        "azioni",
        "prossimi passi",
        "migliorare",
        "strategia"
    ]):
        response_parts.append("\nPriorità operative consigliate:")

        module_scores = [
            ("Finance Oracle AI", finance_score),
            ("Business Health AI", business_health_score),
            ("Customer Oracle AI", customer_score),
            ("Compliance Oracle AI", compliance_score),
            ("Cyber Oracle AI", cyber_score),
        ]

        module_scores.sort(key=lambda x: x[1])

        weakest = module_scores[0]
        response_parts.append(f"- Prima priorità: migliorare {weakest[0]} perché ha score {weakest[1]}/100.")

        if suggestions:
            response_parts.append("\nSuggerimenti specifici:")
            for s in suggestions:
                response_parts.append(f"- {s}")

        if total_revenue <= 0:
            response_parts.append("- Inserire o importare entrate reali.")
        if len(customers) == 0:
            response_parts.append("- Inserire clienti reali.")
        if compliance_score < 65:
            response_parts.append("- Aggiornare documenti, scadenze e compliance.")
        if cyber_score == 50:
            response_parts.append("- Completare il modulo Cyber Oracle AI per ottenere un rischio cyber reale.")

    # SCORE / MODULI
    elif any(word in q for word in [
        "score",
        "punteggio",
        "moduli",
        "valutazione",
        "oracle score"
    ]):
        response_parts.append("\nDettaglio punteggi:")

        response_parts.append(f"- Oracle Score: {oracle_score}/100")
        response_parts.append(f"- Finance Score: {finance_score}/100")
        response_parts.append(f"- Business Health Score: {business_health_score}/100")
        response_parts.append(f"- Customer Score: {customer_score}/100")
        response_parts.append(f"- Compliance Score: {compliance_score}/100")
        response_parts.append(f"- Cyber Score: {cyber_score}/100")

        response_parts.append("\nInterpretazione:")
        response_parts.append("I moduli con punteggio più basso sono quelli su cui intervenire prima.")

    # CYBER
    elif any(word in q for word in [
        "cyber",
        "sicurezza informatica",
        "hacker",
        "vulnerabilità",
        "vulnerabilita",
        "cve",
        "ransomware",
        "attacco",
        "attacchi",
        "minacce",
        "dominio",
        "esposto",
        "esposizione",
        "sicurezza sito",
        "rischio cyber"
    ]):
        response_parts.append("\nAnalisi Cyber Oracle AI:")

        response_parts.append(f"- Cyber Score: {cyber_score}/100")

        if cyber_predictions:
            latest = cyber_predictions[0]

            response_parts.append(f"- Livello cyber: {latest.level}")
            response_parts.append(f"- Probabilità attacco 30 giorni: {latest.attack_probability_30d}%")
            response_parts.append(f"- Probabilità attacco 90 giorni: {latest.attack_probability_90d}%")
            response_parts.append(f"- Trend: {latest.trend}")
            response_parts.append(f"- Rischio principale: {latest.main_risk}")
            response_parts.append(f"- Raccomandazione: {latest.recommendation}")
        else:
            response_parts.append(
                "Non è ancora stata generata una predizione Cyber Oracle AI."
            )
            response_parts.append(
                "Esegui il modulo Cyber Oracle AI per calcolare esposizione, vulnerabilità, minacce e probabilità di attacco."
            )

        response_parts.append(f"\nAsset monitorati: {len(cyber_assets)}")
        response_parts.append(f"Finding rilevati: {len(cyber_findings)}")
        response_parts.append(f"Threat registrate: {len(cyber_threats)}")

        critical_findings = [
            f for f in cyber_findings
            if (f.severity or "").lower() == "critical"
        ]

        high_findings = [
            f for f in cyber_findings
            if (f.severity or "").lower() == "high"
        ]

        if critical_findings:
            response_parts.append("\nFinding critici:")
            for f in critical_findings[:5]:
                response_parts.append(f"- {f.title}: {f.recommendation}")

        if high_findings:
            response_parts.append("\nFinding ad alta severità:")
            for f in high_findings[:5]:
                response_parts.append(f"- {f.title}: {f.recommendation}")

        high_threats = [
            t for t in cyber_threats
            if (t.severity or "").lower() in ["high", "critical"]
        ]

        if high_threats:
            response_parts.append("\nThreat rilevanti:")
            for t in high_threats[:5]:
                response_parts.append(f"- {t.title} ({t.source}): {t.description}")

    # DEFAULT
    else:
        response_parts.append("\nHo analizzato i dati disponibili e questa è la sintesi:")

        response_parts.append(f"- Entrate totali: €{total_revenue}")
        response_parts.append(f"- Operazioni: {total_operations}")
        response_parts.append(f"- Clienti: {len(customers)}")
        response_parts.append(f"- Finance Score: {finance_score}/100")
        response_parts.append(f"- Business Health Score: {business_health_score}/100")
        response_parts.append(f"- Customer Score: {customer_score}/100")
        response_parts.append(f"- Compliance Score: {compliance_score}/100")
        response_parts.append(f"- Cyber Score: {cyber_score}/100")

        response_parts.append(
            "\nPuoi chiedermi ad esempio: "
            "'Quanto ho incassato?', "
            "'Qual è il rischio principale?', "
            "'Come sta andando la mia azienda?', "
            "'Quali sono i punti forti?', "
            "'Cosa devo migliorare?'"
        )

    return "\n".join(response_parts)

def analyze_cyber_risk(company, assets, findings, threats):
    score = 80

    exposure_score = 80
    vulnerability_score = 80
    threat_score = 80
    prediction_score = 80

    risks = []
    strengths = []
    recommendations = []

    if not assets:
        score -= 25
        exposure_score = 50
        risks.append("Nessun asset cyber registrato.")
        recommendations.append("Aggiungere almeno dominio aziendale, email domain o cloud provider.")
    else:
        strengths.append("Sono presenti asset cyber da monitorare.")

    critical_findings = [f for f in findings if (f.severity or "").lower() == "critical"]
    high_findings = [f for f in findings if (f.severity or "").lower() == "high"]
    medium_findings = [f for f in findings if (f.severity or "").lower() == "medium"]

    score -= len(critical_findings) * 25
    score -= len(high_findings) * 15
    score -= len(medium_findings) * 7

    vulnerability_score -= len(critical_findings) * 25
    vulnerability_score -= len(high_findings) * 15
    vulnerability_score -= len(medium_findings) * 7

    if critical_findings:
        risks.append(f"Sono presenti {len(critical_findings)} finding critici.")
    if high_findings:
        risks.append(f"Sono presenti {len(high_findings)} finding ad alta severità.")

    critical_threats = [t for t in threats if (t.severity or "").lower() in ["critical", "critico"]]
    high_threats = [t for t in threats if (t.severity or "").lower() in ["high", "alto"]]

    score -= len(critical_threats) * 15
    score -= len(high_threats) * 8

    threat_score -= len(critical_threats) * 15
    threat_score -= len(high_threats) * 8

    if critical_threats or high_threats:
        risks.append("Sono presenti minacce cyber rilevanti collegate all'azienda.")

    domain_text = (company.domain or "").lower()

    if domain_text:
        strengths.append(f"Dominio aziendale monitorato: {company.domain}.")
    else:
        score -= 10
        exposure_score -= 10
        risks.append("Dominio aziendale non configurato.")
        recommendations.append("Inserire il dominio aziendale nella scheda azienda.")

    score = max(0, min(100, score))
    exposure_score = max(0, min(100, exposure_score))
    vulnerability_score = max(0, min(100, vulnerability_score))
    threat_score = max(0, min(100, threat_score))
    prediction_score = max(0, min(100, prediction_score))

    attack_30d = round(max(5, 100 - score) * 0.65, 2)
    attack_90d = round(max(10, 100 - score) * 0.95, 2)

    if score >= 86:
        level = "ECCELLENTE"
    elif score >= 66:
        level = "FORTE"
    elif score >= 46:
        level = "STABILE"
    elif score >= 26:
        level = "FRAGILE"
    else:
        level = "CRITICO"

    if score >= 70:
        trend = "stable"
        main_risk = "Nessun rischio cyber critico rilevato dai dati disponibili."
    elif score >= 45:
        trend = "worsening"
        main_risk = "Rischio cyber moderato: servono controlli su asset, vulnerabilità e configurazioni."
    else:
        trend = "worsening"
        main_risk = "Rischio cyber elevato: intervenire subito sui finding più gravi."

    if not recommendations:
        recommendations.append("Continuare il monitoraggio periodico degli asset e delle minacce.")

    return {
        "cyber_score": round(score, 2),
        "exposure_score": round(exposure_score, 2),
        "vulnerability_score": round(vulnerability_score, 2),
        "threat_score": round(threat_score, 2),
        "prediction_score": round(prediction_score, 2),
        "level": level,
        "attack_probability_30d": attack_30d,
        "attack_probability_90d": attack_90d,
        "trend": trend,
        "main_risk": main_risk,
        "strengths": strengths,
        "risks": risks,
        "recommendation": " ".join(recommendations)
    }