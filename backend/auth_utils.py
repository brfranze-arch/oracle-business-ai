import hashlib
import secrets


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, hashed = stored_hash.split(":")
        check = hashlib.sha256((salt + password).encode()).hexdigest()
        return check == hashed
    except Exception:
        return False


def generate_token() -> str:
    return secrets.token_urlsafe(48)