import hashlib
import hmac
import os
import jwt
import time

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

def generate_access_token(user_id: str, secret_key: str, expiration: int = 3600) -> str:
    """
    Generate a secure access token for a user.

    Args:
        user_id (str): The unique identifier for the user.
        secret_key (str): A secret key used for signing the token.
        expiration (int): Token expiration time in seconds (default is 1 hour).

    Returns:
        str: A signed access token.
    """

    payload = {
        "user_id": user_id,
        "exp": time.time() + expiration
    }
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

def verify_token(token: str, stored_token: str) -> bool:
    """Verify if the provided token matches the stored token."""
    return hmac.compare_digest(token, stored_token)

def generate_secure_share_token(length: int = 32) -> str:
    """
    Generate a secure random share token.

    Args:
        length (int): The length of the token in bytes (default is 32).

    Returns:
        str: A securely generated hexadecimal token.
    """
    return os.urandom(length).hex()