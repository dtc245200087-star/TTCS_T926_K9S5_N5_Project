from flask import Flask
from .config import Config
from .extensions import db, cors
from .routes import register_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    cors.init_app(app)

    register_routes(app)

    with app.app_context():
        db.create_all()

    return app
