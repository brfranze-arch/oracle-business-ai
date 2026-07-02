from datetime import datetime
import stripe

from billing_models import Subscription, Invoice
from billing_engine import get_user_subscription


def ts_to_datetime(value):
    if not value:
        return None
    return datetime.utcfromtimestamp(value)


def process_stripe_event(event, db):
    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        user_id = int(data["metadata"]["user_id"])
        plan = data["metadata"]["plan"]

        subscription = get_user_subscription(db, user_id)

        stripe_subscription_id = data.get("subscription")
        stripe_customer_id = data.get("customer")

        subscription.plan = plan
        subscription.status = "active"
        subscription.trial = False
        subscription.provider = "stripe"
        subscription.provider_customer = stripe_customer_id
        subscription.provider_subscription = stripe_subscription_id

        if stripe_subscription_id:
            stripe_sub = stripe.Subscription.retrieve(stripe_subscription_id)
            subscription.status = stripe_sub.status
            subscription.renewal_date = ts_to_datetime(stripe_sub.current_period_end)

        db.commit()

        return {"message": "Checkout completato", "plan": plan}

    if event_type == "customer.subscription.updated":
        stripe_subscription_id = data.get("id")

        subscription = db.query(Subscription).filter(
            Subscription.provider_subscription == stripe_subscription_id
        ).first()

        if subscription:
            plan = data.get("metadata", {}).get("plan", subscription.plan)

            subscription.plan = plan
            subscription.status = data.get("status", subscription.status)
            subscription.trial = False
            subscription.renewal_date = ts_to_datetime(data.get("current_period_end"))

            db.commit()

        return {"message": "Subscription aggiornata"}

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

    if event_type in ["invoice.paid", "invoice.payment_failed"]:
        stripe_subscription_id = data.get("subscription")

        subscription = db.query(Subscription).filter(
            Subscription.provider_subscription == stripe_subscription_id
        ).first()

        if subscription:
            invoice = Invoice(
                subscription_id=subscription.id,
                provider="stripe",
                invoice_number=data.get("number"),
                amount=(data.get("amount_paid") or data.get("amount_due") or 0) / 100,
                currency=(data.get("currency") or "eur").upper(),
                status=data.get("status"),
                invoice_url=data.get("hosted_invoice_url"),
            )

            db.add(invoice)
            db.commit()

        return {"message": "Fattura registrata"}

    return {"message": "Evento ignorato", "type": event_type}