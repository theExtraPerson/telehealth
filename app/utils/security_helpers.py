import hashlib
import hmac
import os

def hash_password(password: str) -> str:
    """Hash a password for storing."""
    salt = os.urandom(16)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + pwdhash.hex()

def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a stored password against one provided by user."""
    salt = bytes.fromhex(stored_password[:32])
    stored_pwdhash = stored_password[32:]
    pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
    return hmac.compare_digest(stored_pwdhash, pwdhash.hex())

def generate_token() -> str:
    """Generate a secure random token."""
    return os.urandom(32).hex()

def verify_token(token: str, stored_token: str) -> bool:
    """Verify if the provided token matches the stored token."""
    return hmac.compare_digest(token, stored_token)