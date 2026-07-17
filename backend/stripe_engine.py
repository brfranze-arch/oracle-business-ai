import stripe

from config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeEngine:
    @staticmethod
    def get_price_id(plan: str):
        plan = plan.upper()

        mapping = {
            "PROFESSIONAL": settings.STRIPE_PRICE_PROFESSIONAL,
            "BUSINESS": settings.STRIPE_PRICE_BUSINESS,
            "ENTERPRISE": settings.STRIPE_PRICE_ENTERPRISE,
        }

        return mapping.get(plan)

    @staticmethod
    def create_checkout_session(user, plan: str, return_url: str | None = None):
        price_id = StripeEngine.get_price_id(plan)

        if not price_id:
            raise ValueError("Price ID non configurato per questo piano.")

        portal_url = (return_url or settings.CUSTOMER_PORTAL_URL).rstrip("/")

        session = stripe.checkout.Session.create(
            mode="subscription",
            payment_method_types=["card"],
            customer_email=user.email,
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            success_url=f"{portal_url}?billing=success&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{portal_url}?billing=cancel",
            metadata={
                "user_id": str(user.id),
                "plan": plan.upper(),
            },
            subscription_data={
                "metadata": {
                    "user_id": str(user.id),
                    "plan": plan.upper(),
                }
            },
        )

        return session

    @staticmethod
    def create_customer_portal(customer_id: str):
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"{settings.CUSTOMER_PORTAL_URL}?billing=return",
        )

        return session

    @staticmethod
    def construct_webhook_event(payload, sig_header):
        if not settings.STRIPE_WEBHOOK_SECRET:
            raise ValueError("STRIPE_WEBHOOK_SECRET non configurato.")

        return stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )