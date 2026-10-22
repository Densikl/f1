import json

import click
from flask import Flask
from werkzeug.exceptions import HTTPException

from .api import api
from .models import db
from .seed_data import seed


def create_app(config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///f1.db"
    if config:
        app.config.update(config)

    db.init_app(app)
    app.register_blueprint(api)

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        response = error.get_response()
        response.data = json.dumps({"error": error.description})
        response.content_type = "application/json"
        return response

    @app.cli.command("seed")
    def seed_command():
        """Recreate the database and fill it with sample data."""
        seed()
        click.echo("Database seeded.")

    return app
