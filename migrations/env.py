import logging
from logging.config import fileConfig

from alembic import context
from flask import current_app

# Alembic Config object (from alembic.ini)
config = context.config

# Configure Python logging from .ini file
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# Try to get the Flask app object, or create it
try:
    flask_app = current_app._get_current_object()
except RuntimeError:
    from app import create_app, db
    flask_app = create_app()
    flask_app.app_context().push()
else:
    from app import db

# Get SQLAlchemy metadata from Flask app
target_metadata = db.metadata

# Set SQLAlchemy URL from Flask app's config
def get_engine_url():
    try:
        engine_url = db.engine.url.render_as_string(hide_password=False)
    except AttributeError:
        engine_url = str(db.engine.url)
    return engine_url.replace('%', '%%')  # Escape % for Alembic

config.set_main_option('sqlalchemy.url', get_engine_url())

# Handle offline migrations (no DB connection)
def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = flask_app.config.get('SQLALCHEMY_DATABASE_URI')
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        render_as_batch=True  # Especially useful for SQLite
    )

    with context.begin_transaction():
        context.run_migrations()

# Handle online migrations (with DB connection)
def run_migrations_online():
    """Run migrations in 'online' mode."""

    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    migrate_ext = current_app.extensions.get("migrate")
    conf_args = (migrate_ext.configure_args if migrate_ext else {}) or {}
    conf_args.setdefault("process_revision_directives", process_revision_directives)
    conf_args.setdefault("compare_type", True)
    conf_args.setdefault("render_as_batch", True)  # For SQLite's limitations

    connectable = db.engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            **conf_args
        )

        with context.begin_transaction():
            context.run_migrations()

# Run based on mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
