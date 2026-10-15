"""SQLite persistence for daily construction diary entries."""

import sqlite3
from contextlib import closing
from datetime import datetime, timezone


INITIAL_ENTRIES = (
    ("2026-10-01", "Khu đô thị Bắc Sông Cầu", 1, "08:00", "Thi công móng khu A, thời tiết thuận lợi."),
    ("2026-09-30", "Tòa nhà văn phòng A1", 2, "09:00", "Hoàn thành lắp đặt cốt thép tầng 3."),
)


def initialize_database(database_path):
    with closing(sqlite3.connect(database_path, timeout=10)) as db:
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        db.executescript("""
            CREATE TABLE IF NOT EXISTS nhat_ky_ngay (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cong_trinh TEXT NOT NULL,
                ngay TEXT NOT NULL,
                nguoi_lap_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                nhan_luc_so_nguoi INTEGER,
                nhan_luc_ghi_chu TEXT,
                thiet_bi TEXT,
                thoi_tiet TEXT,
                ghi_chu_thoi_tiet TEXT,
                is_locked INTEGER NOT NULL DEFAULT 0,
                khoa_boi_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                khoa_boi TEXT,
                khoa_luc TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (cong_trinh, ngay)
            );
            CREATE TABLE IF NOT EXISTS nhat_ky_muc (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nhat_ky_ngay_id INTEGER NOT NULL REFERENCES nhat_ky_ngay(id) ON DELETE CASCADE,
                cong_viec_id INTEGER NOT NULL REFERENCES cong_viec(id) ON DELETE RESTRICT,
                gio TEXT NOT NULL,
                noi_dung TEXT NOT NULL,
                nguoi_lap_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS nhat_ky_ngay_lookup ON nhat_ky_ngay(cong_trinh, ngay);
            CREATE INDEX IF NOT EXISTS nhat_ky_muc_work_item ON nhat_ky_muc(cong_viec_id);
            CREATE TABLE IF NOT EXISTS nhat_ky_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cong_trinh TEXT NOT NULL,
                ngay TEXT NOT NULL,
                hanh_dong TEXT NOT NULL CHECK (hanh_dong IN ('lock', 'unlock')),
                ly_do TEXT NOT NULL DEFAULT '',
                thuc_hien_boi_id INTEGER NOT NULL,
                thuc_hien_boi TEXT NOT NULL,
                thuc_hien_luc TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_nhat_ky_audit_day ON nhat_ky_audit(cong_trinh, ngay, id DESC);
        """)
        day_columns = {row[1] for row in db.execute("PRAGMA table_info(nhat_ky_ngay)").fetchall()}
        for column, definition in (
            ("nhan_luc_so_nguoi", "INTEGER"),
            ("nhan_luc_ghi_chu", "TEXT"),
            ("thiet_bi", "TEXT"),
            ("thoi_tiet", "TEXT"),
            ("ghi_chu_thoi_tiet", "TEXT"),
            ("is_locked", "INTEGER NOT NULL DEFAULT 0"),
            ("khoa_boi_id", "INTEGER REFERENCES users(id) ON DELETE SET NULL"),
            ("khoa_boi", "TEXT"),
            ("khoa_luc", "TEXT"),
        ):
            if column not in day_columns:
                db.execute(f"ALTER TABLE nhat_ky_ngay ADD COLUMN {column} {definition}")

        if db.execute("SELECT COUNT(*) FROM nhat_ky_muc").fetchone()[0] == 0:
            first_user = db.execute("SELECT id FROM users ORDER BY id LIMIT 1").fetchone()
            for diary_date, project_name, task_id, entry_time, description in INITIAL_ENTRIES:
                task = db.execute(
                    "SELECT id, cong_trinh FROM cong_viec WHERE id = ?", (task_id,)
                ).fetchone()
                if task and task["cong_trinh"] == project_name:
                    diary_id = _get_or_create_day(db, project_name, diary_date, first_user[0] if first_user else None)
                    db.execute(
                        """INSERT INTO nhat_ky_muc
                           (nhat_ky_ngay_id, cong_viec_id, gio, noi_dung, nguoi_lap_id)
                           VALUES (?, ?, ?, ?, ?)""",
                        (diary_id, task_id, entry_time, description, first_user[0] if first_user else None),
                    )
        db.commit()


def list_entries(database_path, *, project=None, diary_date=None, work_item_id=None):
    conditions, values = [], []
    if project:
        conditions.append("d.cong_trinh = ?")
        values.append(project)
    if diary_date:
        conditions.append("d.ngay = ?")
        values.append(diary_date)
    if work_item_id is not None:
        conditions.append("e.cong_viec_id = ?")
        values.append(work_item_id)
    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    with closing(sqlite3.connect(database_path, timeout=10)) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute(
            """SELECT e.id, d.cong_trinh, d.ngay, d.is_locked,
                      d.khoa_boi, d.khoa_luc, e.cong_viec_id,
                      t.ten AS hang_muc, e.gio, e.noi_dung,
                      COALESCE(u.full_name, 'Tài khoản đã xóa') AS nguoi_lap
               FROM nhat_ky_muc e
               JOIN nhat_ky_ngay d ON d.id = e.nhat_ky_ngay_id
               JOIN cong_viec t ON t.id = e.cong_viec_id
               LEFT JOIN users u ON u.id = e.nguoi_lap_id""" + where_clause +
            " ORDER BY d.ngay DESC, e.gio, e.id",
            values,
        ).fetchall()
        return [dict(row) for row in rows]


def get_daily_summary(database_path, project, diary_date):
    with closing(sqlite3.connect(database_path, timeout=10)) as db:
        db.row_factory = sqlite3.Row
        row = db.execute(
            "SELECT * FROM nhat_ky_ngay WHERE cong_trinh = ? AND ngay = ?",
            (project, diary_date),
        ).fetchone()
        return dict(row) if row else None


def update_daily_summary(database_path, *, project, diary_date, user_id, workforce_count,
                         workforce_notes, equipment, weather, weather_notes):
    with closing(sqlite3.connect(database_path, timeout=10)) as db:
        db.execute("PRAGMA foreign_keys = ON")
        db.execute("BEGIN IMMEDIATE")
        locked = db.execute(
            "SELECT is_locked FROM nhat_ky_ngay WHERE cong_trinh = ? AND ngay = ?",
            (project, diary_date),
        ).fetchone()
        if locked and locked[0]:
            db.rollback()
            return None
        day_id = _get_or_create_day(db, project, diary_date, user_id)
        db.execute(
            """UPDATE nhat_ky_ngay
               SET nhan_luc_so_nguoi = ?, nhan_luc_ghi_chu = ?, thiet_bi = ?,
                   thoi_tiet = ?, ghi_chu_thoi_tiet = ?
               WHERE id = ?""",
            (workforce_count, workforce_notes, equipment, weather, weather_notes, day_id),
        )
        db.commit()
    return get_daily_summary(database_path, project, diary_date)


def create_entry(database_path, *, project, diary_date, task_id, entry_time, description, user_id):
    with sqlite3.connect(database_path, timeout=10) as db:
        db.execute("PRAGMA foreign_keys = ON")
        db.execute("BEGIN IMMEDIATE")
        diary_id = _get_or_create_day(db, project, diary_date, user_id)
        locked = db.execute("SELECT is_locked FROM nhat_ky_ngay WHERE id = ?", (diary_id,)).fetchone()
        if locked and locked[0]:
            db.rollback()
            return None
        cursor = db.execute(
            """INSERT INTO nhat_ky_muc
               (nhat_ky_ngay_id, cong_viec_id, gio, noi_dung, nguoi_lap_id)
               VALUES (?, ?, ?, ?, ?)""",
            (diary_id, task_id, entry_time, description, user_id),
        )
        entry_id = cursor.lastrowid
        db.commit()
    return next((entry for entry in list_entries(database_path, project=project, diary_date=diary_date) if entry["id"] == entry_id), None)


def update_entry(database_path, entry_id, *, task_id, entry_time, description):
    with closing(sqlite3.connect(database_path, timeout=10)) as db:
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        db.execute("BEGIN IMMEDIATE")
        row = db.execute(
            """SELECT d.id, d.is_locked FROM nhat_ky_muc e
               JOIN nhat_ky_ngay d ON d.id = e.nhat_ky_ngay_id WHERE e.id = ?""",
            (entry_id,),
        ).fetchone()
        if not row:
            db.rollback()
            return "not_found"
        if row["is_locked"]:
            db.rollback()
            return "locked"
        db.execute(
            "UPDATE nhat_ky_muc SET cong_viec_id = ?, gio = ?, noi_dung = ? WHERE id = ?",
            (task_id, entry_time, description, entry_id),
        )
        db.commit()
        return "ok"


def is_day_locked(database_path, project, diary_date):
    with closing(sqlite3.connect(database_path, timeout=10)) as db:
        row = db.execute(
            "SELECT is_locked FROM nhat_ky_ngay WHERE cong_trinh = ? AND ngay = ?",
            (project, diary_date),
        ).fetchone()
        return bool(row and row[0])


def lock_day(database_path, project, diary_date, user_id, full_name):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with closing(sqlite3.connect(database_path, timeout=10)) as db:
        db.execute("PRAGMA foreign_keys = ON")
        db.execute("BEGIN IMMEDIATE")
        day_id = _get_or_create_day(db, project, diary_date, user_id)
        if db.execute("SELECT is_locked FROM nhat_ky_ngay WHERE id = ?", (day_id,)).fetchone()[0]:
            db.rollback()
            return False
        db.execute(
            "UPDATE nhat_ky_ngay SET is_locked = 1, khoa_boi_id = ?, khoa_boi = ?, khoa_luc = ? WHERE id = ?",
            (user_id, full_name, now, day_id),
        )
        db.execute(
            """INSERT INTO nhat_ky_audit
               (cong_trinh, ngay, hanh_dong, thuc_hien_boi_id, thuc_hien_boi, thuc_hien_luc)
               VALUES (?, ?, 'lock', ?, ?, ?)""",
            (project, diary_date, user_id, full_name, now),
        )
        db.commit()
        return True


def unlock_day(database_path, project, diary_date, user_id, full_name, reason):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with closing(sqlite3.connect(database_path, timeout=10)) as db:
        db.execute("PRAGMA foreign_keys = ON")
        db.execute("BEGIN IMMEDIATE")
        row = db.execute(
            "SELECT id, is_locked FROM nhat_ky_ngay WHERE cong_trinh = ? AND ngay = ?",
            (project, diary_date),
        ).fetchone()
        if not row or not row[1]:
            db.rollback()
            return False
        db.execute("UPDATE nhat_ky_ngay SET is_locked = 0, khoa_boi_id = NULL, khoa_boi = NULL, khoa_luc = NULL WHERE id = ?", (row[0],))
        db.execute(
            """INSERT INTO nhat_ky_audit
               (cong_trinh, ngay, hanh_dong, ly_do, thuc_hien_boi_id, thuc_hien_boi, thuc_hien_luc)
               VALUES (?, ?, 'unlock', ?, ?, ?, ?)""",
            (project, diary_date, reason, user_id, full_name, now),
        )
        db.commit()
        return True


def list_audit(database_path, project=None, diary_date=None):
    conditions, values = [], []
    if project:
        conditions.append("cong_trinh = ?")
        values.append(project)
    if diary_date:
        conditions.append("ngay = ?")
        values.append(diary_date)
    where = " WHERE " + " AND ".join(conditions) if conditions else ""
    with closing(sqlite3.connect(database_path, timeout=10)) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute("SELECT * FROM nhat_ky_audit" + where + " ORDER BY id DESC LIMIT 200", values).fetchall()
        return [dict(row) for row in rows]


def _get_or_create_day(db, project, diary_date, user_id):
    db.execute(
        """INSERT INTO nhat_ky_ngay (cong_trinh, ngay, nguoi_lap_id)
           VALUES (?, ?, ?) ON CONFLICT(cong_trinh, ngay) DO NOTHING""",
        (project, diary_date, user_id),
    )
    return db.execute(
        "SELECT id FROM nhat_ky_ngay WHERE cong_trinh = ? AND ngay = ?",
        (project, diary_date),
    ).fetchone()[0]
