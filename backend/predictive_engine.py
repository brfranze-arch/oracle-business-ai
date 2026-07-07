def calculate_predictive_ai(
    revenues,
    customers,
    compliance_items,
    cyber_predictions
):
    finance_risk = 50
    customer_risk = 50
    compliance_risk = 50
    cyber_risk = 50

    if len(revenues) == 0:
        finance_risk = 85
    elif len(revenues) < 5:
        finance_risk = 65
    else:
        finance_risk = 35

    if len(customers) == 0:
        customer_risk = 80
    elif len(customers) < 3:
        customer_risk = 60
    else:
        customer_risk = 35

    pending = [
        item for item in compliance_items
        if item.status != "completato"
    ]

    if len(compliance_items) == 0:
        compliance_risk = 70
    elif len(pending) > 0:
        compliance_risk = 60
    else:
        compliance_risk = 25

    if cyber_predictions:
        latest = cyber_predictions[0]
        cyber_risk = latest.attack_probability_30d
    else:
        cyber_risk = 50

    average_risk = (
        finance_risk +
        customer_risk +
        compliance_risk +
        cyber_risk
    ) / 4

    prediction_score = round(100 - average_risk, 2)

    if prediction_score >= 75:
        level = "FORTE"
    elif prediction_score >= 55:
        level = "STABILE"
    elif prediction_score >= 35:
        level = "ATTENZIONE"
    else:
        level = "FRAGILE"

    summary = (
        f"Predizione generata su Finance, Customer, Compliance e Cyber. "
        f"Score predittivo: {prediction_score}/100, livello {level}."
    )

    recommendation = "Continuare il monitoraggio e aggiornare i dati."

    if finance_risk > 60:
        recommendation = "Aumentare il numero di entrate registrate e monitorare il cash flow."

    if customer_risk > 60:
        recommendation = "Ampliare la base clienti e ridurre la dipendenza da pochi clienti."

    if compliance_risk > 60:
        recommendation = "Aggiornare subito gli elementi compliance pendenti o mancanti."

    if cyber_risk > 60:
        recommendation = "Ridurre rapidamente il rischio cyber intervenendo su finding e minacce."

    return {
        "finance_risk": finance_risk,
        "customer_risk": customer_risk,
        "compliance_risk": compliance_risk,
        "cyber_risk": cyber_risk,
        "prediction_score": prediction_score,
        "level": level,
        "summary": summary,
        "recommendation": recommendation
    }