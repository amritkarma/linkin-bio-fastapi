import logging
import os
from fastapi import Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import JWTError, ExpiredSignatureError

from app.database import AsyncSessionLocal
from app.auth import decode_access_token
from app.models import User
from app.crud import (
    get_user_by_username
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

DEBUG = os.getenv("DEBUG", "true").lower() == "true"

logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Async DB Dependency
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# ✅ Async Current User Dependency
async def get_current_user(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Missing or invalid Authorization header")

    token = authorization[7:]
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=401, detail="Invalid token payload")

        user = await get_user_by_username(db, username)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Unexpected error in token decode or DB: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# async def get_current_user(
#     token: str = Depends(oauth2_scheme),
#     db: AsyncSession = Depends(get_db)
# ) -> User:
#     try:
#         payload = decode_access_token(token)
#         username: str = payload.get("sub")
#         if username is None:
#             raise HTTPException(status_code=401, detail="Invalid token")
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")

#     result = await db.execute(select(User).where(User.username == username))
#     user = result.scalars().first()
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")

#     return user
