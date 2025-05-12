import logging
from logging.config import fileConfig
from flask import current_app
from alembic import context

config = context.config

# Configure logging
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

def get_app():
    """Create and configure the Flask application"""
    from app import create_app
    app = create_app()
    return app

def get_database():
    """Get database instance from Flask-SQLAlchemy"""
    # For Flask-SQLAlchemy 3.x+
    if hasattr(current_app, 'extensions') and 'sqlalchemy' in current_app.extensions:
        return current_app.extensions['sqlalchemy']
    raise RuntimeError("SQLAlchemy database not found in Flask app extensions")

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    app = get_app()
    with app.app_context():
        db = get_database()
        url = str(db.engine.url).replace('%', '%%')
        config.set_main_option('sqlalchemy.url', url)
        
        context.configure(
            url=url,
            target_metadata=db.metadata,
            literal_binds=True,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=True
        )

        with context.begin_transaction():
            context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    app = get_app()
    
    with app.app_context():
        db = get_database()
        
        # Configure connection
        connectable = db.engine

        # Set the database URL
        url = str(db.engine.url).replace('%', '%%')
        config.set_main_option('sqlalchemy.url', url)

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=db.metadata,
                compare_type=True,
                compare_server_default=True,
                render_as_batch=True
            )

            with context.begin_transaction():
                context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()