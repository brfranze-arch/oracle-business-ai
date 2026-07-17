from datetime import datetime
import json

from billing_models import Subscription, Invoice
from billing_engine import get_user_subscription


def stripe_to_dict(obj):
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "to_dict_recursive"):
        return obj.to_dict_recursive()
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    return json.loads(str(obj))


def _date_from_timestamp(value):
    try:
        return datetime.utcfromtimestamp(int(value)) if value else None
    except (TypeError, ValueError, OSError):
        return None


def _upsert_invoice(db, subscription, data):
    invoice_number = data.get("number") or data.get("id")
    invoice = db.query(Invoice).filter(
        Invoice.subscription_id == subscription.id,
        Invoice.invoice_number == invoice_number,
    ).first()
    if not invoice:
        invoice = Invoice(subscription_id=subscription.id, provider="stripe", invoice_number=invoice_number)
        db.add(invoice)
    amount = data.get("amount_paid")
    if amount is None:
        amount = data.get("amount_due") or 0
    invoice.amount = amount / 100
    invoice.currency = (data.get("currency") or "eur").upper()
    invoice.status = data.get("status") or "unknown"
    invoice.invoice_url = data.get("hosted_invoice_url") or data.get("invoice_pdf")
    db.commit()


def process_stripe_event(event, db):
    event_type = event["type"]
    data = stripe_to_dict(event["data"]["object"])

    if event_type == "checkout.session.completed":
        metadata = data.get("metadata") or {}
        user_id = metadata.get("user_id")
        if not user_id:
            return {"message": "Checkout senza user_id ignorato"}
        plan = (metadata.get("plan") or "FREE").upper()
        subscription = get_user_subscription(db, int(user_id))
        subscription.plan = plan
        subscription.status = "active"
        subscription.trial = False
        subscription.provider = "stripe"
        subscription.provider_customer = data.get("customer")
        subscription.provider_subscription = data.get("subscription")
        db.commit()
        return {"message": "Checkout completato", "plan": plan}

    if event_type in ["customer.subscription.created", "customer.subscription.updated"]:
        metadata = data.get("metadata") or {}
        user_id = metadata.get("user_id")
        stripe_subscription_id = data.get("id")
        subscription = None
        if stripe_subscription_id:
            subscription = db.query(Subscription).filter(Subscription.provider_subscription == stripe_subscription_id).first()
        if not subscription and user_id:
            subscription = get_user_subscription(db, int(user_id))
        if subscription:
            plan = (metadata.get("plan") or subscription.plan or "PROFESSIONAL").upper()
            subscription.plan = plan
            subscription.status = data.get("status") or subscription.status
            subscription.trial = data.get("status") == "trialing"
            subscription.trial_end = _date_from_timestamp(data.get("trial_end"))
            subscription.provider = "stripe"
            subscription.provider_customer = data.get("customer") or subscription.provider_customer
            subscription.provider_subscription = stripe_subscription_id or subscription.provider_subscription
            subscription.renewal_date = _date_from_timestamp(data.get("current_period_end"))
            subscription.cancel_date = _date_from_timestamp(data.get("cancel_at"))
            db.commit()
        return {"message": "Subscription sincronizzata"}

    if event_type == "customer.subscription.deleted":
        subscription = db.query(Subscription).filter(Subscription.provider_subscription == data.get("id")).first()
        if subscription:
            subscription.plan = "FREE"
            subscription.status = "canceled"
            subscription.cancel_date = datetime.utcnow()
            subscription.renewal_date = None
            db.commit()
        return {"message": "Subscription cancellata"}

    if event_type in ["invoice.paid", "invoice.payment_succeeded", "invoice.payment_failed"]:
        subscription = db.query(Subscription).filter(Subscription.provider_subscription == data.get("subscription")).first()
        if subscription:
            _upsert_invoice(db, subscription, data)
            if event_type == "invoice.payment_failed":
                subscription.status = "past_due"
                db.commit()
        return {"message": "Fattura sincronizzata"}

    if event_type == "customer.updated":
        return {"message": "Cliente Stripe aggiornato"}

    return {"message": "Evento ignorato", "type": event_type}
