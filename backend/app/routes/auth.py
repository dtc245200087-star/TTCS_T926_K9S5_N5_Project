import re
import secrets
import sqlite3
from functools import wraps

from flask import Blueprint, current_app, jsonify, request, session

from ..models import user as users

auth = Blueprint("auth", __name__)
ROLES = {"admin", "manager", "engineer", "viewer"}
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{3,40}$")


def csrf_token():
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get("user_id")
        user = users.get_user(current_app.config["USER_DATABASE"], user_id) if user_id else None
        if not user or not user["is_active"]:
            session.clear()
            return jsonify({"error": "unauthorized", "message": "Vui lòng đăng nhập."}), 401
        request.current_user = user
        return view(*args, **kwargs)

    return wrapped


def roles_required(*allowed_roles):
    def decorate(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if request.current_user["role"] not in allowed_roles:
                return jsonify({"error": "forbidden", "message": "Bạn không có quyền thực hiện thao tác này."}), 403
            return view(*args, **kwargs)

        return wrapped

    return decorate


@auth.get("/csrf")
def get_csrf():
    return jsonify({"csrf_token": csrf_token()})


@auth.post("/login")
def login():
    data = request.get_json(silent=True)
    data = data if isinstance(data, dict) else {}
    username = data.get("username", "")
    password = data.get("password", "")
    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"error": "invalid_credentials", "message": "Tên đăng nhập hoặc mật khẩu không đúng."}), 401

    account = users.get_by_username(current_app.config["USER_DATABASE"], username.strip())
    if not account or not account["is_active"] or not users.verify_password(account, password):
        return jsonify({"error": "invalid_credentials", "message": "Tên đăng nhập hoặc mật khẩu không đúng."}), 401

    session.clear()
    session["user_id"] = account["id"]
    session.permanent = True
    token = csrf_token()
    return jsonify({"user": users.public_user(account), "csrf_token": token})


@auth.post("/logout")
@login_required
def logout():
    session.clear()
    return jsonify({"message": "Đã đăng xuất."})


@auth.get("/me")
@login_required
def me():
    return jsonify({"user": users.public_user(request.current_user), "csrf_token": csrf_token()})


@auth.post("/change-password")
@login_required
def change_password():
    data = request.get_json(silent=True)
    data = data if isinstance(data, dict) else {}
    old_password, new_password = data.get("current_password"), data.get("new_password")
    if not isinstance(old_password, str) or not users.verify_password(request.current_user, old_password):
        return jsonify({"error": "invalid_password", "message": "Mật khẩu hiện tại không đúng."}), 400
    if not isinstance(new_password, str) or len(new_password) < 12 or len(new_password) > 256:
        return jsonify({"error": "invalid_password", "message": "Mật khẩu mới cần từ 12 đến 256 ký tự."}), 400
    users.change_password(current_app.config["USER_DATABASE"], request.current_user["id"], new_password)
    session.clear()
    return jsonify({"message": "Đổi mật khẩu thành công. Vui lòng đăng nhập lại."})


@auth.get("/users")
@roles_required("admin")
def list_users():
    return jsonify([users.public_user(row) for row in users.list_users(current_app.config["USER_DATABASE"])])


@auth.post("/users")
@roles_required("admin")
def add_user():
    data = request.get_json(silent=True)
    data = data if isinstance(data, dict) else {}
    username = data.get("username", "")
    full_name = data.get("full_name", "")
    password = data.get("password", "")
    role = data.get("role", "viewer")
    if not isinstance(username, str) or not USERNAME_PATTERN.fullmatch(username):
        return jsonify({"error": "invalid_username", "message": "Tên đăng nhập cần 3–40 ký tự: chữ không dấu, số, dấu chấm, gạch dưới hoặc gạch ngang."}), 400
    if not isinstance(full_name, str) or not full_name.strip() or len(full_name.strip()) > 120:
        return jsonify({"error": "invalid_full_name", "message": "Họ tên là bắt buộc và tối đa 120 ký tự."}), 400
    if not isinstance(password, str) or len(password) < 12 or len(password) > 256:
        return jsonify({"error": "invalid_password", "message": "Mật khẩu cần từ 12 đến 256 ký tự."}), 400
    if not isinstance(role, str) or role not in ROLES:
        return jsonify({"error": "invalid_role", "message": "Vai trò không hợp lệ."}), 400
    try:
        user = users.create_user(current_app.config["USER_DATABASE"], username.strip(), full_name.strip(), password, role)
    except sqlite3.IntegrityError:
        return jsonify({"error": "username_exists", "message": "Tên đăng nhập đã tồn tại."}), 409
    return jsonify(user), 201


@auth.patch("/users/<int:user_id>")
@roles_required("admin")
def edit_user(user_id):
    target = users.get_user(current_app.config["USER_DATABASE"], user_id)
    if not target:
        return jsonify({"error": "not_found", "message": "Không tìm thấy tài khoản."}), 404
    data = request.get_json(silent=True)
    data = data if isinstance(data, dict) else {}
    role = data.get("role")
    full_name = data.get("full_name")
    is_active = data.get("is_active")
    if role is not None and (not isinstance(role, str) or role not in ROLES):
        return jsonify({"error": "invalid_role", "message": "Vai trò không hợp lệ."}), 400
    if full_name is not None and (not isinstance(full_name, str) or not full_name.strip() or len(full_name.strip()) > 120):
        return jsonify({"error": "invalid_full_name", "message": "Họ tên là bắt buộc và tối đa 120 ký tự."}), 400
    if is_active is not None and not isinstance(is_active, bool):
        return jsonify({"error": "invalid_status", "message": "is_active phải là true hoặc false."}), 400

    changed_role = role if role is not None else target["role"]
    changed_active = is_active if is_active is not None else bool(target["is_active"])
    if target["id"] == request.current_user["id"] and (changed_role != target["role"] or not changed_active):
        return jsonify({"error": "self_change_forbidden", "message": "Không thể tự hạ quyền hoặc khóa tài khoản đang đăng nhập."}), 409
    if target["role"] == "admin" and (changed_role != "admin" or not changed_active):
        active_admins = sum(1 for row in users.list_users(current_app.config["USER_DATABASE"]) if row["role"] == "admin" and row["is_active"])
        if active_admins <= 1:
            return jsonify({"error": "last_admin", "message": "Không thể hạ quyền hoặc khóa quản trị viên hoạt động cuối cùng."}), 409
    user = users.update_user(
        current_app.config["USER_DATABASE"], user_id,
        full_name=full_name.strip() if full_name is not None else None,
        role=role, is_active=is_active,
    )
    return jsonify(user)
