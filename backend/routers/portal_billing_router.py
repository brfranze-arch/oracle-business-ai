from __future__ import annotations

from datetime import datetime
from typing import Any

import stripe
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from billing_engine import get_user_subscription
from billing_models import Invoice, Plan, Subscription
from config import settings
from deps import get_current_user, get_db
from models import User
from stripe_engine import StripeEngine

router = APIRouter(prefix="/api/portal/billing", tags=["Customer Portal Billing"])


class CheckoutRequest(BaseModel):
    return_url: str | None = None


class CheckoutCompleteRequest(BaseModel):
    session_id: str


def _safe_return_url(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip().rstrip("/")
    if value.startswith("https://") or value.startswith("http://127.0.0.1") or value.startswith("http://localhost"):
        return value
    raise HTTPException(status_code=400, detail="URL di ritorno non valida")


def _as_dict(value):
    """
    Converte in modo sicuro gli oggetti restituiti da Stripe
    in normali dizionari Python.

    StripeObject non deve essere convertito tramite dict(value),
    perché alcune versioni della libreria tentano di accedere
    agli elementi tramite indici numerici e generano KeyError: 0.
    """
    if value is None:
        return {}

    if isinstance(value, dict):
        return value

    to_dict_recursive = getattr(value, "to_dict_recursive", None)
    if callable(to_dict_recursive):
        return to_dict_recursive()

    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        return to_dict()

    items = getattr(value, "items", None)
    if callable(items):
        return {key: item for key, item in items()}

    return {}

def _timestamp(value):
    if not value:
        return None
    try:
        return datetime.utcfromtimestamp(int(value))
    except (TypeError, ValueError, OSError):
        return None


def _iso(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return value.isoformat() if value else None


def _plan_from_price(price_id: str | None, fallback: str = "FREE") -> str:
    mapping = {
        settings.STRIPE_PRICE_PROFESSIONAL: "PROFESSIONAL",
        settings.STRIPE_PRICE_BUSINESS: "BUSINESS",
        settings.STRIPE_PRICE_ENTERPRISE: "ENTERPRISE",
    }
    return mapping.get(price_id, fallback.upper())


def _sync_subscription(db: Session, subscription: Subscription) -> dict:
    if not subscription.provider_subscription:
        return {"synced": False, "reason": "Nessun abbonamento Stripe collegato"}

    remote = _as_dict(stripe.Subscription.retrieve(
        subscription.provider_subscription,
        expand=["default_payment_method", "items.data.price"],
    ))
    items = ((_as_dict(remote.get("items"))).get("data") or [])
    first_item = _as_dict(items[0]) if items else {}
    price = _as_dict(first_item.get("price"))
    plan = _plan_from_price(price.get("id"), subscription.plan)

    subscription.plan = plan
    subscription.status = remote.get("status") or subscription.status
    subscription.provider = "stripe"
    subscription.provider_customer = remote.get("customer") or subscription.provider_customer
    subscription.renewal_date = _timestamp(remote.get("current_period_end"))
    subscription.cancel_date = _timestamp(remote.get("cancel_at"))
    subscription.trial = bool(remote.get("trial_end") and remote.get("status") == "trialing")
    subscription.trial_end = _timestamp(remote.get("trial_end"))
    db.commit()
    db.refresh(subscription)
    return {"synced": True, "stripe_subscription": remote}


def _payment_method(subscription: Subscription, remote_subscription: dict | None = None) -> dict | None:
    payment = _as_dict((remote_subscription or {}).get("default_payment_method"))
    if not payment and subscription.provider_customer:
        customer = _as_dict(stripe.Customer.retrieve(
            subscription.provider_customer,
            expand=["invoice_settings.default_payment_method"],
        ))
        payment = _as_dict(_as_dict(customer.get("invoice_settings")).get("default_payment_method"))
    card = _as_dict(payment.get("card")) if payment else {}
    if not card:
        return None
    return {
        "type": payment.get("type") or "card",
        "brand": card.get("brand"),
        "last4": card.get("last4"),
        "exp_month": card.get("exp_month"),
        "exp_year": card.get("exp_year"),
    }


def _invoice_payload(item: dict) -> dict:
    amount = item.get("amount_paid")
    if amount is None:
        amount = item.get("amount_due") or 0
    return {
        "id": item.get("id"),
        "number": item.get("number") or item.get("id"),
        "status": item.get("status") or "unknown",
        "amount": amount / 100,
        "currency": (item.get("currency") or "eur").upper(),
        "created_at": _iso(_timestamp(item.get("created"))),
        "hosted_invoice_url": item.get("hosted_invoice_url"),
        "invoice_pdf": item.get("invoice_pdf"),
    }


@router.get("/summary")
def billing_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    subscription = get_user_subscription(db, current_user.id)
    plan = db.query(Plan).filter(Plan.name == subscription.plan).first()
    remote = None
    sync_error = None
    if subscription.provider == "stripe" and subscription.provider_subscription:
        try:
            sync_result = _sync_subscription(db, subscription)
            remote = sync_result.get("stripe_subscription")
            plan = db.query(Plan).filter(Plan.name == subscription.plan).first()
        except stripe.error.StripeError as exc:
            sync_error = str(exc)

    return {
        "plan": subscription.plan,
        "status": subscription.status,
        "provider": subscription.provider,
        "trial": subscription.trial,
        "trial_end": _iso(subscription.trial_end),
        "renewal_date": _iso(subscription.renewal_date),
        "cancel_date": _iso(subscription.cancel_date),
        "cancel_at_period_end": bool((remote or {}).get("cancel_at_period_end")),
        "price_month": plan.price_month if plan else 0,
        "currency": "EUR",
        "stripe_customer_connected": bool(subscription.provider_customer),
        "stripe_subscription_connected": bool(subscription.provider_subscription),
        "payment_method": _payment_method(subscription, remote),
        "sync_error": sync_error,
    }


@router.post("/sync")
def sync_billing(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    subscription = get_user_subscription(db, current_user.id)
    if subscription.provider != "stripe" or not subscription.provider_subscription:
        return {"message": "Nessun abbonamento Stripe da sincronizzare", "synced": False}
    try:
        _sync_subscription(db, subscription)
        return {"message": "Abbonamento sincronizzato", "synced": True, "plan": subscription.plan, "status": subscription.status}
    except stripe.error.StripeError as exc:
        raise HTTPException(status_code=502, detail=f"Stripe non disponibile: {exc}")


@router.post("/portal-session")
def portal_session(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    subscription = get_user_subscription(db, current_user.id)
    if not subscription.provider_customer:
        raise HTTPException(status_code=409, detail="Nessun cliente Stripe collegato. Completa prima un checkout di test.")
    try:
        session = StripeEngine.create_customer_portal(subscription.provider_customer)
        return {"portal_url": session.url}
    except stripe.error.StripeError as exc:
        raise HTTPException(status_code=502, detail=f"Impossibile aprire Stripe Customer Portal: {exc}")


@router.post("/checkout/complete")
def checkout_complete(payload: CheckoutCompleteRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        session = _as_dict(stripe.checkout.Session.retrieve(
            payload.session_id,
            expand=["subscription", "customer"],
        ))
    except stripe.error.StripeError as exc:
        raise HTTPException(status_code=502, detail=f"Impossibile verificare il checkout Stripe: {exc}")

    metadata = _as_dict(session.get("metadata"))
    if str(metadata.get("user_id")) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Checkout non associato all'utente autenticato")

    if session.get("status") != "complete":
        raise HTTPException(status_code=409, detail="Checkout Stripe non ancora completato")

    remote_subscription = _as_dict(session.get("subscription"))
    subscription_id = remote_subscription.get("id") or session.get("subscription")
    customer = _as_dict(session.get("customer"))
    customer_id = customer.get("id") or session.get("customer")
    if not subscription_id or not customer_id:
        raise HTTPException(status_code=409, detail="Stripe non ha restituito customer o abbonamento")

    subscription = get_user_subscription(db, current_user.id)
    subscription.provider = "stripe"
    subscription.provider_customer = str(customer_id)
    subscription.provider_subscription = str(subscription_id)
    subscription.trial = False
    db.commit()
    db.refresh(subscription)

    synced = _sync_subscription(db, subscription)
    return {
        "message": "Pagamento verificato e abbonamento sincronizzato",
        "synced": synced.get("synced", False),
        "plan": subscription.plan,
        "status": subscription.status,
    }



@router.post("/checkout/{plan}")
def checkout(plan: str, payload: CheckoutRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    normalized = plan.upper()
    selected = db.query(Plan).filter(Plan.name == normalized, Plan.active == True).first()
    if not selected or normalized == "FREE":
        raise HTTPException(status_code=400, detail="Piano Stripe non valido")
    subscription = get_user_subscription(db, current_user.id)
    if subscription.provider_customer:
        raise HTTPException(status_code=409, detail="Cliente Stripe già collegato: usa Gestisci abbonamento per upgrade o downgrade")
    try:
        session = StripeEngine.create_checkout_session(current_user, normalized, _safe_return_url(payload.return_url))
        return {"checkout_url": session.url, "session_id": session.id}
    except (stripe.error.StripeError, ValueError) as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@router.get("/invoices")
def invoices(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    subscription = get_user_subscription(db, current_user.id)
    if subscription.provider_customer:
        try:
            remote = stripe.Invoice.list(customer=subscription.provider_customer, limit=24)
            return [_invoice_payload(_as_dict(item)) for item in remote.data]
        except stripe.error.StripeError:
            pass
    rows = db.query(Invoice).filter(Invoice.subscription_id == subscription.id).order_by(Invoice.created_at.desc()).limit(24).all()
    return [{
        "id": row.id,
        "number": row.invoice_number or f"LOCAL-{row.id}",
        "status": row.status,
        "amount": row.amount,
        "currency": row.currency,
        "created_at": _iso(row.created_at),
        "hosted_invoice_url": row.invoice_url,
        "invoice_pdf": None,
    } for row in rows]
