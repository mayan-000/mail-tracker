from flask import Flask
import logging
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")

    from .auth import auth_bp
    from .routes import routes_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(routes_bp)

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    return app
