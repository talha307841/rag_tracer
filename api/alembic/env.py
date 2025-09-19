from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from app.core.database import Base
import app.models.tracing

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

# ✅ Use DATABASE_URL from environment
url = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/rag_tracer")

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        {"sqlalchemy.url": url},  # ✅ inject our URL
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()


