from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import SessionLocal
from models import User, UserSession

security = HTTPBearer(auto_error=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    if not credentials:
        return None

    token = credentials.credentials

    session = db.query(UserSession).filter(
        UserSession.token == token
    ).first()

    if not session:
        return None

    user = db.query(User).filter(
        User.id == session.user_id
    ).first()

    return user
