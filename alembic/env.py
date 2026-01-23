import os
import sys
from pathlib import Path
from logging.config import fileConfig
from dotenv import load_dotenv

from sqlalchemy import create_engine, pool
from alembic import context

# Ensure parent directory is in path for imports
_parent_dir = Path(__file__).parent.parent.parent
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))

# Load environment variables
load_dotenv()

# Import your Base metadata here
from app.models import Base

config = context.config

# Determine database URL based on DEBUG mode
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

if DEBUG:
    # Use SQLite for development (sync driver for Alembic)
    database_url = "sqlite:///./dev.db"
else:
    # Use PostgreSQL for production
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME")
    
    if not all([db_user, db_password, db_host, db_port, db_name]):
        raise RuntimeError("One or more database environment variables are not set!")
    
    # Construct sync DB URL (use psycopg3 for Alembic - sync driver)
    database_url = f"postgresql+psycopg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Set it for Alembic config
config.set_main_option("sqlalchemy.url", database_url)

# Set up Python logging config from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import your model's MetaData object for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (generates SQL scripts)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (apply directly to DB)."""
    url = config.get_main_option("sqlalchemy.url")
    
    # Use NullPool for PostgreSQL, but not for SQLite
    pool_class = pool.NullPool if url.startswith("postgresql") else None
    
    connectable = create_engine(
        url,
        poolclass=pool_class,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Optional: enable type comparison for autogenerate
            compare_type=True,
            # SQLite-specific configuration
            render_as_batch=url.startswith("sqlite"),
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
