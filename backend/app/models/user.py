"""SQLite-backed user storage and password helpers for the API."""

import sqlite3
from contextlib import closing
from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash


def connect(database_path):
    connection = sqlite3.connect(database_path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(database_path):
    with closing(connect(database_path)) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL COLLATE NOCASE UNIQUE,
            full_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('admin', 'manager', 'engineer', 'viewer')),
            is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )""")
        db.commit()


def public_user(row):
    if row is None:
        return None
    return {
        "id": row["id"],
        "username": row["username"],
        "full_name": row["full_name"],
        "role": row["role"],
        "is_active": bool(row["is_active"]),
        "created_at": row["created_at"],
    }


def get_user(database_path, user_id):
    with closing(connect(database_path)) as db:
        return db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def get_by_username(database_path, username):
    with closing(connect(database_path)) as db:
        return db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()


def list_users(database_path):
    with closing(connect(database_path)) as db:
        return db.execute(
            "SELECT * FROM users ORDER BY username COLLATE NOCASE"
        ).fetchall()


def count_users(database_path):
    with closing(connect(database_path)) as db:
        return db.execute("SELECT COUNT(*) FROM users").fetchone()[0]


def create_user(database_path, username, full_name, password, role):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with closing(connect(database_path)) as db:
        cursor = db.execute(
            """INSERT INTO users (username, full_name, password_hash, role, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (username, full_name, generate_password_hash(password), role, now, now),
        )
        db.commit()
        return public_user(db.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone())


def update_user(database_path, user_id, *, full_name=None, role=None, is_active=None):
    fields, values = [], []
    if full_name is not None:
        fields.append("full_name = ?")
        values.append(full_name)
    if role is not None:
        fields.append("role = ?")
        values.append(role)
    if is_active is not None:
        fields.append("is_active = ?")
        values.append(int(is_active))
    if fields:
        fields.append("updated_at = ?")
        values.extend([datetime.now(timezone.utc).isoformat(timespec="seconds"), user_id])
        with closing(connect(database_path)) as db:
            db.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = ?", values)
            db.commit()
    return public_user(get_user(database_path, user_id))


def change_password(database_path, user_id, password):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with closing(connect(database_path)) as db:
        db.execute(
            "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
            (generate_password_hash(password), now, user_id),
        )
        db.commit()


def verify_password(user, password):
    return bool(user and check_password_hash(user["password_hash"], password))
