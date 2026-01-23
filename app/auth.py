from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext
from app.config import (
    SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
)

# Use Argon2 for password hashing
try:
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
except Exception as e:
    # Fallback to bcrypt if argon2 is not available (should not happen with proper install)
    import warnings
    warnings.warn(f"Argon2 not available, falling back to bcrypt: {e}")
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password using Argon2."""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        raise ValueError(f"Password hashing failed: {e}")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        # Log error but don't expose details
        import logging
        logging.getLogger(__name__).error(f"Password verification error: {e}")
        return False

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if "sub" not in payload:
            raise JWTError("Token missing subject (sub)")
        if payload.get("type") != "access":
            raise JWTError("Invalid token type")
        return payload
    except ExpiredSignatureError as e:
        raise ExpiredSignatureError("Token has expired") from e
    except JWTError as e:
        raise JWTError("Token is invalid") from e

def decode_refresh_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if "sub" not in payload:
            raise JWTError("Token missing subject (sub)")
        if payload.get("type") != "refresh":
            raise JWTError("Invalid token type")
        return payload
    except ExpiredSignatureError as e:
        raise ExpiredSignatureError("Refresh token has expired") from e
    except JWTError as e:
        raise JWTError("Invalid refresh token") from e
