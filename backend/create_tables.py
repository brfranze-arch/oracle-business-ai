from database import Base, engine
import models
import billing_models
import tenant_models
import openai_models

import digital_twin_models
import osint_models
import predictive_models
import agents_models
import portal_models
import portal_license_models

Base.metadata.create_all(bind=engine)

from database import SessionLocal
from portal_seed import seed_portal_catalog
with SessionLocal() as db:
    seed_portal_catalog(db)

print("Tabelle aggiornate senza cancellare il database.")
