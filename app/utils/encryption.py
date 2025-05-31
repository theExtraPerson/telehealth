from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from app.config import settings

def generate_fernet_key():
    """Generate a new Fernet-compatible key"""
    return Fernet.generate_key().decode()

def get_fernet_key():
    """
    Get or create a valid Fernet key from settings.
    If invalid, generates a new one and updates settings.
    """
    key = settings.ENCRYPTION_KEY
    
    # If no key exists, generate one
    if not key:
        key = generate_fernet_key()
        settings.ENCRYPTION_KEY = key
        return key.encode()
    
    # If key exists but isn't valid Fernet key
    try:
        # Test if key is valid
        Fernet(key.encode())
        return key.encode()
    except ValueError:
        # Generate new key if existing one is invalid
        new_key = generate_fernet_key()
        settings.ENCRYPTION_KEY = new_key
        return new_key.encode()

# Initialize cipher suite with validated key
cipher_suite = Fernet(get_fernet_key())

def encrypt_data(data: str) -> str:
    """Encrypt string data"""
    if not data:
        return data
    try:
        encrypted_data = cipher_suite.encrypt(data.encode())
        return encrypted_data.decode()
    except Exception as e:
        raise ValueError(f"Encryption failed: {str(e)}")

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt string data"""
    if not encrypted_data:
        return encrypted_data
    try:
        decrypted_data = cipher_suite.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")