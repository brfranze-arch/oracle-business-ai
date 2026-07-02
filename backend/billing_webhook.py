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


def process_stripe_event(event, db):
    event_type = event["type"]
    data = stripe_to_dict(event["data"]["object"])

    if event_type == "checkout.session.completed":
        metadata = data.get("metadata") or {}

        user_id = int(metadata.get("user_id"))
        plan = (metadata.get("plan") or "FREE").upper()

        subscription = get_user_subscription(db, user_id)

        subscription.plan = plan
        subscription.status = "active"
        subscription.trial = False
        subscription.provider = "stripe"
        subscription.provider_customer = data.get("customer")
        subscription.provider_subscription = data.get("subscription")

        db.commit()

        return {"message": "Checkout completato", "plan": plan}

    if event_type == "customer.subscription.created":
        metadata = data.get("metadata") or {}
        user_id = metadata.get("user_id")
        plan = (metadata.get("plan") or "PROFESSIONAL").upper()

        if user_id:
            subscription = get_user_subscription(db, int(user_id))
            subscription.plan = plan
            subscription.status = data.get("status") or "active"
            subscription.trial = False
            subscription.provider = "stripe"
            subscription.provider_customer = data.get("customer")
            subscription.provider_subscription = data.get("id")
            db.commit()

        return {"message": "Subscription creata"}

    if event_type == "customer.subscription.updated":
        stripe_subscription_id = data.get("id")

        subscription = db.query(Subscription).filter(
            Subscription.provider_subscription == stripe_subscription_id
        ).first()

        if subscription:
            metadata = data.get("metadata") or {}
            plan = (metadata.get("plan") or subscription.plan).upper()

            subscription.plan = plan
            subscription.status = data.get("status") or subscription.status
            subscription.trial = False
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