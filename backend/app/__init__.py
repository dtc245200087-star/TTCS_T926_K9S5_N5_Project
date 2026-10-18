import hmac
import os
from pathlib import Path

from flask import Flask, jsonify, request, session
from flask_cors import CORS

from .extensions import db  # Bổ sung import db từ extensions
from .models import cong_viec as tasks
from .models import user as users
from .routes.api import api
from .routes.auth import auth
from .routes.cong_viec_routes import cong_viec_bp

def create_app(test_config=None):
    app = Flask(__name__)

    # Đường dẫn file CSDL SQLite
    db_path = Path(__file__).resolve().parents[1] / "instance" / "app.db"
    os.makedirs(db_path.parent, exist_ok=True)

    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY") or os.urandom(24),
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL") or f"sqlite:///{db_path}",
        USER_DATABASE=os.environ.get(
            "USER_DATABASE",
            str(Path(__file__).resolve().parents[1] / "instance" / "users.db"),
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        PERMANENT_SESSION_LIFETIME=60 * 60 * 8,
    )

    if test_config:
        app.config.update(test_config)

    user_database = Path(app.config["USER_DATABASE"])
    user_database.parent.mkdir(parents=True, exist_ok=True)
    tasks.initialize_database(str(user_database))

    # 1. Khởi tạo SQLAlchemy với app
    db.init_app(app)
    CORS(app)

    # 2. Đăng ký các Blueprint
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(auth, url_prefix='/api/auth')
    app.register_blueprint(cong_viec_bp)  # Đăng ký Blueprint quản lý công việc S-25

    return app
