# from flask import Flask, g, app
from app import create_app, db
from dotenv import load_dotenv

load_dotenv()

app = create_app()

with app.app_context():
    db.create_all()

@app.before_request
def log_context_push():
    app.logger.debug(f"Pushing context: {app.app_context()}")

@app.teardown_request
def log_context_pop(exception=None):
    app.logger.debug(f"Popping context: {app.app_context()}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')