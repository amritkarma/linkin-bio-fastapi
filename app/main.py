import os
import sys
import uuid
import logging
from pathlib import Path
from typing import List, Optional

# Ensure parent directory is in path (for when run directly by uvicorn reloader)
_parent_dir = Path(__file__).parent.parent
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))

from fastapi import (
    FastAPI, Depends, HTTPException, status, Header,
    UploadFile, File, Form, Request
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv
import filetype

# 🛡️ Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# 🌩️ Cloudinary
import cloudinary
import cloudinary.uploader

from app import models, schemas
from app.schemas import (
    ProfileOut, Token, UserCreate, UserLogin,
    LinkCreate, LinkOut, LinkUpdate,
    UserOut, UserUpdate
)
from app.crud import (
    get_user_by_username, create_user, authenticate_user, get_user_links,
    get_links_by_user_id, get_link_by_id, create_link, update_link, delete_link,
    update_user_profile
)
from app.auth import (
    create_access_token, create_refresh_token,
    decode_access_token, decode_refresh_token
)
from jose import JWTError, ExpiredSignatureError
from app.dependencies import get_current_user, get_db

# === Load Environment Variables ===
load_dotenv()

DEBUG = os.getenv("DEBUG", "true").lower() == "true"
USE_CLOUDINARY = not DEBUG
PORT = int(os.getenv("PORT", 8000))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# === Media Setup ===
MEDIA_DIR = "media"
AVATAR_DIR = os.path.join(MEDIA_DIR, "avatars")
if DEBUG and not USE_CLOUDINARY:
    os.makedirs(AVATAR_DIR, exist_ok=True)

if USE_CLOUDINARY:
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True
    )

# === Logging ===
# Set logging level - reduce aiosqlite verbosity in production
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Reduce verbosity of aiosqlite and sqlalchemy in production
if not DEBUG:
    logging.getLogger('aiosqlite').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# === FastAPI App ===
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Link-in-Bio API",
    version="1.0.0",
    description="API backend for Link-in-Bio app"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if DEBUG and not USE_CLOUDINARY:
    app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

# === Database Initialization ===
@app.on_event("startup")
async def startup_event():
    """Create database tables on startup (development only)."""
    if DEBUG:
        try:
            from app.database import async_engine, Base
            from app import models  # Import models to register them with Base
            
            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Database tables verified/created successfully")
        except Exception as e:
            logger.warning(f"⚠️ Could not create tables (they may already exist): {e}")

# === Dependency: Current Authenticated User ===
# async def get_current_user(
#     authorization: str = Header(None),
#     db: AsyncSession = Depends(get_db)
# ):
#     if not authorization or not authorization.startswith("Bearer "):
#         raise HTTPException(
#             status_code=401, detail="Missing or invalid Authorization header")

#     token = authorization[7:]
#     try:
#         payload = decode_access_token(token)
#         username = payload.get("sub")
#         if not username:
#             raise HTTPException(
#                 status_code=401, detail="Invalid token payload")

#         user = await get_user_by_username(db, username)
#         if not user:
#             raise HTTPException(status_code=401, detail="User not found")

#         return user
#     except Exception as e:
#         logger.error(f"Token decode error: {e}")
#         raise HTTPException(status_code=401, detail="Invalid token")

# === Auth Endpoints ===
@app.post("/register", response_model=Token)
@limiter.limit("5/minute")
async def register(user: UserCreate, request: Request, db: AsyncSession = Depends(get_db)):
    try:
        # Check if username already exists
        existing_user = await get_user_by_username(db, user.username)
        if existing_user:
            raise HTTPException(
                status_code=400, detail="Username already registered")
        
        # Create new user
        user_obj = await create_user(db, user)
        
        # Generate tokens
        access_token = create_access_token({"sub": user_obj.username})
        refresh_token = create_refresh_token({"sub": user_obj.username})
        
        logger.info(f"User registered successfully: {user_obj.username}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Registration failed: {str(e)}"
        )

@app.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(form: UserLogin, request: Request, db: AsyncSession = Depends(get_db)):
    try:
        user = await authenticate_user(db, form.username, form.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access_token = create_access_token({"sub": user.username})
        refresh_token = create_refresh_token({"sub": user.username})
        
        logger.info(f"User logged in successfully: {user.username}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Login failed. Please try again."
        )

@app.post("/refresh", response_model=Token)
@limiter.limit("20/minute")
async def refresh_token(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        body = await request.json()
        refresh_token_value = body.get("refresh_token")
        if not refresh_token_value:
            raise HTTPException(status_code=401, detail="Refresh token required")
        
        payload = decode_refresh_token(refresh_token_value)
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        user = await get_user_by_username(db, username)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        access_token = create_access_token({"sub": user.username})
        new_refresh_token = create_refresh_token({"sub": user.username})
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token has expired")
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

# === Link Endpoints ===
@app.get("/users/{username}/links", response_model=List[LinkOut])
async def list_user_links(username: str, limit: int = 10, offset: int = 0, db: AsyncSession = Depends(get_db)):
    return await get_user_links(db, username, limit, offset)

@app.get("/links", response_model=List[LinkOut])
async def get_my_links(user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_links_by_user_id(db, user.id)

@app.post("/links", response_model=LinkOut)
async def add_link(link: LinkCreate, user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await create_link(db, user.id, link)

@app.get("/links/{link_id}", response_model=LinkOut)
async def get_single_link(link_id: int, user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    link = await get_link_by_id(db, link_id, user.id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return link

@app.put("/links/{link_id}", response_model=LinkOut)
async def edit_link(link_id: int, link_data: LinkUpdate, user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    updated = await update_link(db, link_id, user.id, link_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Link not found")
    return updated

@app.delete("/links/{link_id}")
async def delete_user_link(link_id: int, user: models.User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    deleted = await delete_link(db, link_id, user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Link not found")
    return {"detail": "Deleted"}

# === Profile Endpoints ===
@app.get("/me", response_model=UserOut)
async def get_me(user: models.User = Depends(get_current_user)):
    return user

@app.patch("/me", response_model=UserOut)
async def update_me(
    bio: Optional[str] = Form(""),
    avatar: Optional[UploadFile] = File(None),
    user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    avatar_url = user.avatar_url

    if avatar:
        try:
            file_content = await avatar.read()
            kind = filetype.guess(file_content)

            if not kind or kind.mime not in ["image/png", "image/jpeg"]:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid image format. Only PNG and JPEG allowed."
                )

            ext = f".{kind.extension}" if kind else ".jpg"
            filename = f"{user.username}_{uuid.uuid4().hex}{ext}"

            if USE_CLOUDINARY:
                try:
                    upload_result = cloudinary.uploader.upload(
                        file_content,
                        folder="avatars",
                        public_id=filename,
                        resource_type="image"
                    )
                    avatar_url = upload_result["secure_url"]
                except Exception as e:
                    logger.error(f"Cloudinary upload failed: {e}")
                    raise HTTPException(status_code=500, detail="Cloudinary upload failed")
            else:
                filepath = os.path.join(AVATAR_DIR, filename)
                try:
                    with open(filepath, "wb") as buffer:
                        buffer.write(file_content)
                    avatar_url = f"/media/avatars/{filename}"
                except Exception as e:
                    logger.error(f"Local file save failed: {e}")
                    raise HTTPException(status_code=500, detail="Failed to save avatar locally")

        except Exception as e:
            logger.error(f"Avatar processing failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Avatar upload failed")

    try:
        return await update_user_profile(
            db,
            user.id,
            schemas.UserUpdate(bio=bio, avatar_url=avatar_url),
        )
    except Exception as e:
        logger.error(f"Profile update failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to update profile")


@app.get("/users/{username}", response_model=ProfileOut)
async def get_user_profile(username: str, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    links = await get_links_by_user_id(db, user.id)
    return {
        "username": user.username,
        "bio": user.bio,
        "avatar_url": user.avatar_url,
        "links": links
    }

@app.get("/")
def read_root():
    return {"Hello": "World"}
