import logging
from logging.config import fileConfig

from alembic import context
from flask import current_app
from app import create_app, db  # update with your actual module name

# Alembic config
config = context.config


# Logging setup
fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")

# Create the Flask app and manage context correctly
app = create_app()

with app.app_context():
    # Set DB URL from the Flask SQLAlchemy instance
    config.set_main_option("sqlalchemy.url", str(db.engine.url))

    target_metadata = db.metadata

    def run_migrations_offline():
        """Run migrations in 'offline' mode."""
        url = config.get_main_option("sqlalchemy.url")
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
        )

        with context.begin_transaction():
            context.run_migrations()

    def run_migrations_online():
        """Run migrations in 'online' mode."""
        connectable = db.engine

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                render_as_batch=True  # useful for SQLite
            )

            with context.begin_transaction():
                context.run_migrations()

    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()
