"""SQLite persistence and locking rules for construction diary entries."""

from contextlib import closing
from datetime import datetime, timezone

from .user import connect


def initialize_database(database_path):
    with closing(connect(database_path)) as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS nhat_ky (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ngay TEXT NOT NULL,
                cong_trinh TEXT NOT NULL,
                noi_dung TEXT NOT NULL,
                nguoi_lap TEXT NOT NULL,
                nguoi_lap_id INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_nhat_ky_ngay ON nhat_ky(ngay);
            CREATE TABLE IF NOT EXISTS nhat_ky_khoa_ngay (
                ngay TEXT PRIMARY KEY,
                khoa_boi_id INTEGER NOT NULL,
                khoa_boi TEXT NOT NULL,
                khoa_luc TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS nhat_ky_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ngay TEXT NOT NULL,
                hanh_dong TEXT NOT NULL CHECK (hanh_dong IN ('lock', 'unlock')),
                ly_do TEXT NOT NULL DEFAULT '',
                thuc_hien_boi_id INTEGER NOT NULL,
                thuc_hien_boi TEXT NOT NULL,
                thuc_hien_luc TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_nhat_ky_audit_ngay ON nhat_ky_audit(ngay, id DESC);
        """)
        if db.execute("SELECT COUNT(*) FROM nhat_ky").fetchone()[0] == 0:
            now = datetime.now(timezone.utc).isoformat(timespec="seconds")
            db.executemany("""
                INSERT INTO nhat_ky (ngay, cong_trinh, noi_dung, nguoi_lap, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [
                ("2026-10-01", "Khu đô thị Bắc Sông Cầu", "Thi công móng khu A, thời tiết thuận lợi.", "Nguyễn Văn An", now, now),
                ("2026-09-30", "Tòa nhà văn phòng A1", "Hoàn thành lắp đặt cốt thép tầng 3.", "Trần Minh Đức", now, now),
            ])
        db.commit()


def _public_entry(row):
    return {
        "id": row["id"],
        "ngay": row["ngay"],
        "cong_trinh": row["cong_trinh"],
        "noi_dung": row["noi_dung"],
        "nguoi_lap": row["nguoi_lap"],
        "is_locked": bool(row["khoa_ngay"]),
        "khoa_boi": row["khoa_boi"],
        "khoa_luc": row["khoa_luc"],
    }


def list_entries(database_path):
    with closing(connect(database_path)) as db:
        rows = db.execute("""
            SELECT n.*, k.ngay AS khoa_ngay, k.khoa_boi, k.khoa_luc
            FROM nhat_ky n LEFT JOIN nhat_ky_khoa_ngay k ON k.ngay = n.ngay
            ORDER BY n.ngay DESC, n.id DESC
        """).fetchall()
        return [_public_entry(row) for row in rows]


def add_entry(database_path, *, day, project, content, author, author_id):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with closing(connect(database_path)) as db:
        db.execute("BEGIN IMMEDIATE")
        if db.execute("SELECT 1 FROM nhat_ky_khoa_ngay WHERE ngay = ?", (day,)).fetchone():
            db.rollback()
            return None
        cursor = db.execute("""
            INSERT INTO nhat_ky (ngay, cong_trinh, noi_dung, nguoi_lap, nguoi_lap_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (day, project, content, author, author_id, now, now))
        db.commit()
        return cursor.lastrowid


def update_entry(database_path, entry_id, *, project, content):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with closing(connect(database_path)) as db:
        db.execute("BEGIN IMMEDIATE")
        entry = db.execute("SELECT ngay FROM nhat_ky WHERE id = ?", (entry_id,)).fetchone()
        if not entry:
            db.rollback()
            return "not_found"
        if db.execute("SELECT 1 FROM nhat_ky_khoa_ngay WHERE ngay = ?", (entry["ngay"],)).fetchone():
            db.rollback()
            return "locked"
        db.execute("UPDATE nhat_ky SET cong_trinh = ?, noi_dung = ?, updated_at = ? WHERE id = ?",
                   (project, content, now, entry_id))
        db.commit()
        return "ok"


def lock_day(database_path, day, user_id, full_name):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with closing(connect(database_path)) as db:
        db.execute("BEGIN IMMEDIATE")
        if db.execute("SELECT 1 FROM nhat_ky_khoa_ngay WHERE ngay = ?", (day,)).fetchone():
            db.rollback()
            return False
        db.execute("INSERT INTO nhat_ky_khoa_ngay (ngay, khoa_boi_id, khoa_boi, khoa_luc) VALUES (?, ?, ?, ?)",
                   (day, user_id, full_name, now))
        db.execute("INSERT INTO nhat_ky_audit (ngay, hanh_dong, thuc_hien_boi_id, thuc_hien_boi, thuc_hien_luc) VALUES (?, 'lock', ?, ?, ?)",
                   (day, user_id, full_name, now))
        db.commit()
        return True


def unlock_day(database_path, day, user_id, full_name, reason):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with closing(connect(database_path)) as db:
        db.execute("BEGIN IMMEDIATE")
        if not db.execute("SELECT 1 FROM nhat_ky_khoa_ngay WHERE ngay = ?", (day,)).fetchone():
            db.rollback()
            return False
        db.execute("DELETE FROM nhat_ky_khoa_ngay WHERE ngay = ?", (day,))
        db.execute("INSERT INTO nhat_ky_audit (ngay, hanh_dong, ly_do, thuc_hien_boi_id, thuc_hien_boi, thuc_hien_luc) VALUES (?, 'unlock', ?, ?, ?, ?)",
                   (day, reason, user_id, full_name, now))
        db.commit()
        return True


def list_audit(database_path, day=None):
    with closing(connect(database_path)) as db:
        if day:
            rows = db.execute("SELECT * FROM nhat_ky_audit WHERE ngay = ? ORDER BY id DESC", (day,)).fetchall()
        else:
            rows = db.execute("SELECT * FROM nhat_ky_audit ORDER BY id DESC LIMIT 200").fetchall()
        return [dict(row) for row in rows]
