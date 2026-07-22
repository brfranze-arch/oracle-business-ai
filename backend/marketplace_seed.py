from sqlalchemy.orm import Session
from marketplace_models import MarketplaceCategory, MarketplaceModule

CATEGORIES = [
    ("ai-automation", "AI e Automazione", "Agenti, automazioni e strumenti intelligenti.", "✦", 10),
    ("finance", "Finance", "Controllo economico, previsioni e reportistica.", "€", 20),
    ("security", "Cyber Security", "Protezione, monitoraggio e compliance.", "◆", 30),
    ("productivity", "Produttività", "Workflow, documenti e collaborazione.", "▤", 40),
]
MODULES = [
    ("cashflow-forecast", "Previsione Cash Flow", "finance", "Previsioni finanziarie a 90 giorni e scenari automatici.", "Analizza entrate e uscite, genera scenari previsionali e segnala tempestivamente possibili tensioni di liquidità.", "€", 0, "FREE", "FREE", True),
    ("executive-ai-brief", "Executive AI Brief", "ai-automation", "Brief direzionale automatico con priorità e rischi.", "Crea una sintesi giornaliera per il management partendo dai dati dell'intero workspace.", "✦", 19, "MONTHLY", "PROFESSIONAL", True),
    ("cyber-exposure-monitor", "Cyber Exposure Monitor", "security", "Monitoraggio continuo di domini, SSL, DNS e vulnerabilità.", "Estende Cyber Oracle con controlli periodici dell'esposizione pubblica e raccomandazioni operative.", "◆", 29, "MONTHLY", "BUSINESS", True),
    ("document-ai", "Document AI", "productivity", "Classificazione ed estrazione dati da documenti aziendali.", "Organizza documenti, estrae campi rilevanti e prepara i dati per i moduli Orizzonte360.", "▤", 49, "ONE_TIME", "PROFESSIONAL", False),
]

def seed_marketplace(db: Session):
    category_by_slug = {}
    for slug, name, description, icon, sort_order in CATEGORIES:
        row = db.query(MarketplaceCategory).filter(MarketplaceCategory.slug == slug).first()
        if not row:
            row = MarketplaceCategory(slug=slug, name=name, description=description, icon=icon, sort_order=sort_order)
            db.add(row); db.flush()
        category_by_slug[slug] = row
    for slug, name, category_slug, short, description, icon, price, billing_type, required_plan, featured in MODULES:
        row = db.query(MarketplaceModule).filter(MarketplaceModule.slug == slug).first()
        if not row:
            db.add(MarketplaceModule(slug=slug, name=name, category_id=category_by_slug[category_slug].id,
                short_description=short, description=description, icon=icon, price=price,
                billing_type=billing_type, required_plan=required_plan, featured=featured, status="PUBLISHED", active=True))
    db.commit()
