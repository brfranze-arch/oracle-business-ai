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

Base.metadata.create_all(bind=engine)

print("Tabelle aggiornate senza cancellare il database.")
