def clamp(value, min_value=0, max_value=100):
    return max(min_value, min(max_value, float(value)))


def level_from_score(score):
    if score >= 80:
        return "ECCELLENTE"
    if score >= 65:
        return "FORTE"
    if score >= 50:
        return "STABILE"
    if score >= 35:
        return "ATTENZIONE"
    return "FRAGILE"


def build_digital_twin(
    revenues,
    customers,
    compliance_items,
    cyber_predictions,
    osint_scans,
    predictive_insights,
    agent_runs,
):
    total_revenue = sum(r.amount for r in revenues)

    finance_index = 30
    if total_revenue > 0:
        finance_index = 55
    if len(revenues) >= 5:
        finance_index = 70
    if len(revenues) >= 10:
        finance_index = 82

    customer_index = 30
    if len(customers) > 0:
        customer_index = 55
    if len(customers) >= 3:
        customer_index = 70
    if len(customers) >= 8:
        customer_index = 82

    compliance_index = 50
    if compliance_items:
        completed = [i for i in compliance_items if i.status == "completato"]
        compliance_index = (len(completed) / len(compliance_items)) * 100

    cyber_index = 50
    if cyber_predictions:
        cyber_index = cyber_predictions[0].cyber_score

    osint_index = 50
    if osint_scans:
        osint_index = osint_scans[0].exposure_score

    predictive_index = 50
    if predictive_insights:
        predictive_index = predictive_insights[0].prediction_score

    agents_index = 50
    if agent_runs:
        high = [a for a in agent_runs if a.priority == "high"]
        medium = [a for a in agent_runs if a.priority == "medium"]
        agents_index = 85 - (len(high) * 15) - (len(medium) * 6)

    indexes = [
        finance_index,
        customer_index,
        compliance_index,
        cyber_index,
        osint_index,
        predictive_index,
        agents_index,
    ]

    twin_score = round(sum(indexes) / len(indexes), 2)
    twin_score = clamp(twin_score)
    level = level_from_score(twin_score)

    current_state = (
        f"Il Digital Twin rileva revenue pari a €{round(total_revenue, 2)}, "
        f"{len(customers)} clienti, {len(compliance_items)} elementi compliance e "
        f"un livello complessivo {level}."
    )

    forecast_state = (
        "La previsione aggregata dipende dalla qualità dei dati disponibili. "
        "Aggiornare costantemente Finance, Customer, Compliance e Cyber migliora l'affidabilità del Twin."
    )

    scenario_summary = (
        "Scenario base: mantenendo i trend attuali, Oracle consiglia di concentrare l'attenzione "
        "sui moduli con indice più basso."
    )

    weakest = min(
        [
            ("Finance", finance_index),
            ("Customer", customer_index),
            ("Compliance", compliance_index),
            ("Cyber", cyber_index),
            ("OSINT", osint_index),
            ("Predictive", predictive_index),
            ("Agents", agents_index),
        ],
        key=lambda x: x[1],
    )

    recommendation = f"Priorità operativa: migliorare il modulo {weakest[0]} perché ha l'indice più basso ({round(weakest[1], 2)}/100)."

    return {
        "twin_score": twin_score,
        "level": level,
        "finance_index": round(clamp(finance_index), 2),
        "customer_index": round(clamp(customer_index), 2),
        "compliance_index": round(clamp(compliance_index), 2),
        "cyber_index": round(clamp(cyber_index), 2),
        "osint_index": round(clamp(osint_index), 2),
        "predictive_index": round(clamp(predictive_index), 2),
        "agents_index": round(clamp(agents_index), 2),
        "current_state": current_state,
        "forecast_state": forecast_state,
        "scenario_summary": scenario_summary,
        "recommendation": recommendation,
    }
