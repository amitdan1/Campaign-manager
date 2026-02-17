"""
Alembic environment configuration.
Uses our existing SQLAlchemy Base and engine configuration.
"""

import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Add project root to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import Config  # noqa: E402
from services.database import Base  # noqa: E402

# Import all models so they register with Base.metadata
import models.lead  # noqa: F401, E402
import models.campaign  # noqa: F401, E402
import models.interaction  # noqa: F401, E402
import models.proposal  # noqa: F401, E402
import models.brand_asset  # noqa: F401, E402
import models.chat_message  # noqa: F401, E402
import models.agent_memory  # noqa: F401, E402

# Alembic Config object
config = context.config

# Override sqlalchemy.url from our Config
config.set_main_option("sqlalchemy.url", Config.DATABASE_URL)

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # Required for SQLite ALTER TABLE support
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # Required for SQLite ALTER TABLE support
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
