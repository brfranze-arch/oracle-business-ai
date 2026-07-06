import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:admin123@localhost:5432/oracle_business_ai"
    )

    FRONTEND_URL = os.getenv(
        "FRONTEND_URL",
        "http://127.0.0.1:5500"
    )

    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")

    STRIPE_PRICE_PROFESSIONAL = os.getenv("STRIPE_PRICE_PROFESSIONAL", "")
    STRIPE_PRICE_BUSINESS = os.getenv("STRIPE_PRICE_BUSINESS", "")
    STRIPE_PRICE_ENTERPRISE = os.getenv("STRIPE_PRICE_ENTERPRISE", "")

    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")


settings = Settings()