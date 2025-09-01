import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

# Load environment variables
load_dotenv()

DEBUG = os.getenv("DEBUG", "true").lower() == "true"

if DEBUG:
    DATABASE_URL = "sqlite+aiosqlite:///./dev.db"  # Use async SQLite driver
    connect_args = {"check_same_thread": False}
else:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME")

    DATABASE_URL = (
        f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    connect_args = {}

# ✅ Create async engine
# async_engine = create_async_engine(DATABASE_URL, echo=True, connect_args=connect_args)
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=5,
    max_overflow=0,
    connect_args=connect_args,
)


# ✅ Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, expire_on_commit=False, autoflush=False, autocommit=False
)


# ✅ Async-compatible Base
class Base(AsyncAttrs, DeclarativeBase):
    pass
