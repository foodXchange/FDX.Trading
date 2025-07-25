from logging.config import fileConfig
import os
import sys
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

# Import your models' Base
from app.models.base import Base

# Import all models to ensure they're registered with Base
from app.models.user import User
from app.models.supplier import Supplier
from app.models.rfq import RFQ
from app.models.quote import Quote
from app.models.email import Email
from app.models.product import Product
from app.models.activity_log import ActivityLog
from app.models.company import Company
from app.models.contact import Contact
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.order_status_history import OrderStatusHistory
from app.models.notification import Notification
from app.models.communication_log import CommunicationLog
from app.models.invoice import Invoice
from app.models.payment import Payment

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def get_database_url():
    """Get database URL from environment or use default"""
    # Try to get from environment variable
    url = os.getenv("DATABASE_URL")
    
    if not url:
        # Fallback to development database
        url = "sqlite:///./foodxchange.db"
        print("Warning: DATABASE_URL not set, using SQLite for development")
    
    return url

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # Get the database URL
    url = get_database_url()
    
    # Update the configuration with the URL
    configuration = config.get_section(config.config_ini_section)
    configuration['sqlalchemy.url'] = url
    
    # Handle SQLite vs PostgreSQL differences
    if url.startswith("sqlite"):
        # SQLite specific configuration
        connectable = engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            connect_args={"check_same_thread": False}
        )
    else:
        # PostgreSQL configuration
        connectable = engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()