from flask import Flask
import os

from .api.main import api_bp
from .views.main import views_bp


def create_app():
    app = Flask(__name__)
    # Ensure directories exist
    os.makedirs("memorias", exist_ok=True)
    app.register_blueprint(api_bp)
    app.register_blueprint(views_bp)
    return app
