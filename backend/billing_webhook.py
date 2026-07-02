from datetime import datetime

from billing_models import Subscription, Invoice
from billing_engine import get_user_subscription


def process_stripe_event(event, db):
    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        metadata = data.get("metadata", {})

        user_id = int(metadata.get("user_id"))
        plan = metadata.get("plan", "FREE").upper()

        subscription = get_user_subscription(db, user_id)

        subscription.plan = plan
        subscription.status = "active"
        subscription.trial = False
        subscription.provider = "stripe"
        subscription.provider_customer = data.get("customer")
        subscription.provider_subscription = data.get("subscription")

        db.commit()

        return {"message": "Checkout completato", "plan": plan}

    if event_type == "customer.subscription.deleted":
        stripe_subscription_id = data.get("id")

        subscription = db.query(Subscription).filter(
            Subscription.provider_subscription == stripe_subscription_id
        ).first()

        if subscription:
            subscription.plan = "FREE"
            subscription.status = "canceled"
            subscription.cancel_date = datetime.utcnow()
            db.commit()

        return {"message": "Subscription cancellata"}

    if event_type in ["invoice.paid", "invoice.payment_succeeded", "invoice.payment_failed"]:
        stripe_subscription_id = data.get("subscription")

        subscription = db.query(Subscription).filter(
            Subscription.provider_subscription == stripe_subscription_id
        ).first()

        if subscription:
            amount = data.get("amount_paid") or data.get("amount_due") or 0

            invoice = Invoice(
                subscription_id=subscription.id,
                provider="stripe",
                invoice_number=data.get("number"),
                amount=amount / 100,
                currency=(data.get("currency") or "eur").upper(),
                status=data.get("status"),
                invoice_url=data.get("hosted_invoice_url"),
            )

            db.add(invoice)
            db.commit()

        return {"message": "Fattura registrata"}

    return {"message": "Evento ignorato", "type": event_type}