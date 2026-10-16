"""SQLite persistence for daily construction diary entries."""

import sqlite3
from contextlib import closing


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
                client_uid TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS nhat_ky_anh (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nhat_ky_muc_id INTEGER NOT NULL REFERENCES nhat_ky_muc(id) ON DELETE CASCADE,
                filename TEXT NOT NULL,
                thumbnail_filename TEXT,
                upload_id TEXT UNIQUE,
                ghi_chu TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS nhat_ky_ngay_lookup ON nhat_ky_ngay(cong_trinh, ngay);
            CREATE INDEX IF NOT EXISTS nhat_ky_muc_work_item ON nhat_ky_muc(cong_viec_id);
        """)
        day_columns = {row[1] for row in db.execute("PRAGMA table_info(nhat_ky_ngay)").fetchall()}
        entry_columns = {row[1] for row in db.execute("PRAGMA table_info(nhat_ky_muc)").fetchall()}
        image_columns = {row[1] for row in db.execute("PRAGMA table_info(nhat_ky_anh)").fetchall()}
        if "client_uid" not in entry_columns:
            db.execute("ALTER TABLE nhat_ky_muc ADD COLUMN client_uid TEXT")
        db.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS nhat_ky_muc_client_uid ON nhat_ky_muc(client_uid)"
        )
        if "thumbnail_filename" not in image_columns:
            db.execute("ALTER TABLE nhat_ky_anh ADD COLUMN thumbnail_filename TEXT")
        if "upload_id" not in image_columns:
            db.execute("ALTER TABLE nhat_ky_anh ADD COLUMN upload_id TEXT")
        db.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS nhat_ky_anh_upload_id ON nhat_ky_anh(upload_id)"
        )
        for column, definition in (
            ("nhan_luc_so_nguoi", "INTEGER"),
            ("nhan_luc_ghi_chu", "TEXT"),
            ("thiet_bi", "TEXT"),
            ("thoi_tiet", "TEXT"),
            ("ghi_chu_thoi_tiet", "TEXT"),
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