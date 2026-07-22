import argparse
import getpass
import sys

from database import Base, SessionLocal, engine
from models import User, UserSession
from auth_utils import hash_password

ALLOWED_ROLES = {"superadmin", "admin", "marketplace_manager", "partner_manager", "support"}

def main() -> int:
    parser = argparse.ArgumentParser(description="Crea o aggiorna un utente Enterprise Orizzonte360")
    parser.add_argument("--email", default="admin@orizzonte360.local")
    parser.add_argument("--name", default="Orizzonte360 Super Admin")
    parser.add_argument("--role", default="superadmin", choices=sorted(ALLOWED_ROLES))
    args = parser.parse_args()

    email = args.email.strip().lower()
    name = args.name.strip()
    if not email or "@" not in email:
        print("ERRORE: email non valida")
        return 2

    password = getpass.getpass("Nuova password amministratore: ")
    confirm = getpass.getpass("Conferma password: ")
    if password != confirm:
        print("ERRORE: le password non coincidono")
        return 2
    if len(password) < 10:
        print("ERRORE: usa almeno 10 caratteri")
        return 2

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        user = db.query(User).filter(User.email == email).first()
        created = user is None
        if created:
            user = User(email=email, name=name, password_hash=hash_password(password), role=args.role)
            db.add(user)
            db.flush()
        else:
            user.name = name or user.name
            user.password_hash = hash_password(password)
            user.role = args.role
            db.query(UserSession).filter(UserSession.user_id == user.id).delete(synchronize_session=False)
        db.commit()
        db.refresh(user)
        action = "creato" if created else "aggiornato"
        print(f"OK: utente Enterprise {action}")
        print(f"Email: {user.email}")
        print(f"Ruolo: {user.role}")
        print("Le sessioni precedenti dell'utente sono state invalidate.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
