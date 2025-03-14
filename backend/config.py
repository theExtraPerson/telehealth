from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Configuration settings for the Flask backend application.
    """
    # The secret key to use for the Flask app
    SECRET_KEY: str

    # The database URL to use for the SQLAlchemy connection
    SQLALCHEMY_DATABASE_URL: str

    # The title to display in the navigation bar
    TITLE: str = "Flask Skeleton"

    # The tagline to display in the navigation bar
    TAGLINE: str = "A skeleton Flask application"

    class Config:
        """
        Configuration options for the Settings class.
        """
        env_file = ".env"
        case_sensitive = True
# Configuration settings