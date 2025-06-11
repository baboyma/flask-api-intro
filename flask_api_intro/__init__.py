import os
from flask import Flask, request, jsonify
from flask_api_intro.models import db  # Assuming you have a models module with db initialized
from config import Config

def create_app(config=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(config)

    db.init_app(app)  # Assuming you have a db module to initialize the database

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Import and register blueprints or routes here if needed
    # Example: from . import routes
    return app

# app = Flask(__name__)


# if __name__ == '__main__':
#     app.run(host="127.0.0.1", debug=True)