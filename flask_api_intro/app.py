import os
from . import create_app
from flask_api_intro.routes.books import bp_books
from flask_api_intro.routes.api import bp_api
from config import Config


def main():
    """Main function to define and run the Flask application."""

    # Create the Flask application instance
    app = create_app(config = Config)

    if not os.path.exists(Config.DATABASE_NAME):
        with app.app_context():
            from flask_api_intro.models import db
            db.create_all()

    # Main routes
    @app.route('/', methods=['GET'])
    def index():
        return {"message": "Hello, World!"}, 200

    @app.route('/api', methods=['GET'])
    def main():
        return {"message": "Hello, RESTFull API!"}, 200

    # Registering blueprints
    app.register_blueprint(bp_books, url_prefix='/api/')
    app.register_blueprint(bp_api, url_prefix='/')

    # Running the app
    app.run(host="127.0.1", port=5000, debug=True)

# If this script is run directly, start the Flask application
if __name__ == '__main__':
    main()
