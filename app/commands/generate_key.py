import click
from cryptography.fernet import Fernet
from flask.cli import with_appcontext

@click.command('generate-key')
@with_appcontext
def generate_key():
    """Generate a new encryption key"""
    key = Fernet.generate_key().decode()
    click.echo(f"New encryption key: {key}")
    click.echo("Add this to your .env file as ENCRYPTION_KEY=")