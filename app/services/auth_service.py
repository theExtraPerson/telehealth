import datetime
from time import timezone
from typing import Any

import jwt
from flask import request
from passlib.context import CryptContext

# Secret key for JWT encoding and decoding
SECRET_KEY = "your_secret_key"

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: datetime.timedelta = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> Any | None:
        try:
            decoded_jwt = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return decoded_jwt if decoded_jwt["exp"] >= datetime.datetime.utcnow().timestamp() else None
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None


def get_current_user():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        var = None
    try:
        token = auth_header.split(" ")[1]
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None