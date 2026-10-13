import hmac
import os
from pathlib import Path

from flask import Flask, jsonify, request, session
from flask_cors import CORS

from .models import user as users
from .models import cong_viec as tasks
from .models import milestone as milestone_data
from .routes.api import api
from .routes.auth import auth


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY") or os.urandom(32),
        USER_DATABASE=os.environ.get(
            "USER_DATABASE",
            str(Path(__file__).resolve().parents[1] / "instance" / "users.db"),
        ),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "false").lower() == "true",
        PERMANENT_SESSION_LIFETIME=60 * 60 * 8,
        JSON_AS_ASCII=False,
        MAX_CONTENT_LENGTH=1024 * 1024,
        FRONTEND_ORIGINS=[origin.strip() for origin in os.environ.get(
            "FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
        ).split(",") if origin.strip()],
    )
    if test_config:
        app.config.update(test_config)

    db_path = Path(app.config["USER_DATABASE"])
    db_path.parent.mkdir(parents=True, exist_ok=True)
    users.initialize_database(str(db_path))
    tasks.initialize_database(str(db_path))
    milestone_data.initialize_database(str(db_path))
    if users.count_users(str(db_path)) == 0:
        username = os.environ.get("INITIAL_ADMIN_USERNAME", "admin")
        password = os.environ.get("INITIAL_ADMIN_PASSWORD")
        if not password or len(password) < 12 or len(password) > 256:
            raise RuntimeError(
                "Chưa có tài khoản. Hãy đặt INITIAL_ADMIN_PASSWORD (12–256 ký tự) "
                "để tạo quản trị viên đầu tiên."
            )
        if len(username) < 3 or len(username) > 40 or any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-" for ch in username):
            raise RuntimeError("INITIAL_ADMIN_USERNAME chỉ nhận 3–40 ký tự chữ không dấu, số, dấu chấm, gạch dưới hoặc gạch ngang.")
        users.create_user(
            str(db_path), username, os.environ.get("INITIAL_ADMIN_FULL_NAME", "Quản trị viên"), password, "admin"
        )

    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["FRONTEND_ORIGINS"]}},
        supports_credentials=True,
        allow_headers=["Content-Type", "X-CSRF-Token"],
        methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    )

    @app.before_request
    def protect_state_changes():
        if request.method in {"POST", "PATCH", "PUT", "DELETE"}:
            if not session.get("csrf_token") and not session.get("user_id") and request.endpoint != "auth.login":
                return None
            expected = session.get("csrf_token", "")
            provided = request.headers.get("X-CSRF-Token", "")
            if not expected or not provided or not hmac.compare_digest(expected, provided):
                return jsonify({"error": "csrf_failed", "message": "Phiên làm việc không hợp lệ. Hãy tải lại trang."}), 400

    app.register_blueprint(auth, url_prefix="/api/auth")
    app.register_blueprint(api, url_prefix="/api")
    return app
