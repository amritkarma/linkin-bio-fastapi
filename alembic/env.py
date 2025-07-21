import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from app.database import Base  # ✅ Import your async Base
from app.models import *       # ✅ Ensure all models are imported

from dotenv import load_dotenv
import os

load_dotenv()

# Load config
config = context.config
fileConfig(config.config_file_name)

# Set SQLAlchemy URL
# DATABASE_URL = os.getenv("DATABASE_URL")

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

    DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

if DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL not set in environment")

config.set_main_option("sqlalchemy.url", DATABASE_URL)

target_metadata = Base.metadata

# === Async run ===
def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.begin() as conn:
        await conn.run_sync(do_run_migrations)

def main():
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        asyncio.run(run_migrations_online())

main()