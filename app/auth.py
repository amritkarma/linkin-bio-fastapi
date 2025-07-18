from datetime import datetime, timedelta
from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if "sub" not in payload:
            raise JWTError("Token missing subject (sub)")
        return payload
    except ExpiredSignatureError as e:
        raise ExpiredSignatureError("Token has expired") from e
    except JWTError as e:
        raise JWTError("Token is invalid") from e

# def decode_access_token(token: str):
#     return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
