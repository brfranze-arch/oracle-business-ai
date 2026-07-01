from database import Base, engine
import models
import billing_models

Base.metadata.create_all(bind=engine)

print("Tabelle aggiornate senza cancellare il database.")