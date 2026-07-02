from datetime import datetime
import stripe

from billing_models import Subscription, Invoice
from billing_engine import get_user_subscription


def ts_to_datetime(value):
    try:
        if not value:
            return None
        return datetime.utcfromtimestamp(int(value))
    except Exception:
        return None


def safe_get(obj, key, default=None):
    try:
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)
    except Exception:
        return default


def process_stripe_event(event, db):
    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        metadata = safe_get(data, "metadata", {}) or {}

        user_id = int(metadata.get("user_id"))
        plan = metadata.get("plan", "FREE").upper()

        subscription = get_user_subscription(db, user_id)

        stripe_subscription_id = safe_get(data, "subscription")
        stripe_customer_id = safe_get(data, "customer")

        subscription.plan = plan
        subscription.status = "active"
        subscription.trial = False
        subscription.provider = "stripe"
        subscription.provider_customer = stripe_customer_id
        subscription.provider_subscription = stripe_subscription_id

        try:
            if stripe_subscription_id:
                stripe_sub = stripe.Subscription.retrieve(stripe_subscription_id)
                subscription.status = safe_get(stripe_sub, "status", "active")

                current_period_end = safe_get(stripe_sub, "current_period_end")
                subscription.renewal_date = ts_to_datetime(current_period_end)
        except Exception:
            pass

        db.commit()

        return {"message": "Checkout completato", "plan": plan}

    if event_type == "customer.subscription.created":
        metadata = safe_get(data, "metadata", {}) or {}
        user_id = metadata.get("user_id")
        plan = metadata.get("plan", "PROFESSIONAL").upper()

        if user_id:
            subscription = get_user_subscription(db, int(user_id))

            subscription.plan = plan
            subscription.status = safe_get(data, "status", "active")
            subscription.trial = False
            subscription.provider = "stripe"
            subscription.provider_customer = safe_get(data, "customer")
            subscription.provider_subscription = safe_get(data, "id")
            subscription.renewal_date = ts_to_datetime(
                safe_get(data, "current_period_end")
            )

            db.commit()

        return {"message": "Subscription creata"}

    if event_type == "customer.subscription.updated":
        stripe_subscription_id = safe_get(data, "id")

        subscription = db.query(Subscription).filter(
            Subscription.provider_subscription == stripe_subscription_id
        ).first()

        if subscription:
            metadata = safe_get(data, "metadata", {}) or {}
            plan = metadata.get("plan", subscription.plan)

            subscription.plan = plan
            subscription.status = safe_get(data, "status", subscription.status)
            subscription.trial = False
            subscription.renewal_date = ts_to_datetime(
                safe_get(data, "current_period_end")
            )

            db.commit()

        return {"message": "Subscription aggiornata"}

    if event_type == "customer.subscription.deleted":
        stripe_subscription_id = safe_get(data, "id")

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
        stripe_subscription_id = safe_get(data, "subscription")

        subscription = db.query(Subscription).filter(
            Subscription.provider_subscription == stripe_subscription_id
        ).first()

        if subscription:
            invoice = Invoice(
                subscription_id=subscription.id,
                provider="stripe",
                invoice_number=safe_get(data, "number"),
                amount=(safe_get(data, "amount_paid", 0) or safe_get(data, "amount_due", 0) or 0) / 100,
                currency=(safe_get(data, "currency", "eur") or "eur").upper(),
                status=safe_get(data, "status"),
                invoice_url=safe_get(data, "hosted_invoice_url"),
            )

            db.add(invoice)
            db.commit()

        return {"message": "Fattura registrata"}

    return {"message": "Evento ignorato", "type": event_type}