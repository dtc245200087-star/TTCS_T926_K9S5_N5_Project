
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
                mua_ca_ngay INTEGER NOT NULL DEFAULT 0,
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
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS nhat_ky_muc_client_uid ON nhat_ky_muc(client_uid)")

        image_columns = {row[1] for row in db.execute("PRAGMA table_info(nhat_ky_anh)").fetchall()}

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
            ("mua_ca_ngay", "INTEGER NOT NULL DEFAULT 0"),
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

            """SELECT e.id, e.client_uid, d.cong_trinh, d.ngay, e.cong_viec_id,

            """SELECT e.id, d.cong_trinh, d.ngay, e.cong_viec_id,

                      t.ten AS hang_muc, e.gio, e.noi_dung,
                      COALESCE(u.full_name, 'Tài khoản đã xóa') AS nguoi_lap
               FROM nhat_ky_muc e
               JOIN nhat_ky_ngay d ON d.id = e.nhat_ky_ngay_id
               JOIN cong_viec t ON t.id = e.cong_viec_id
               LEFT JOIN users u ON u.id = e.nguoi_lap_id""" + where_clause +
            " ORDER BY d.ngay DESC, e.gio, e.id",
            values,
        ).fetchall()
        entries = [dict(row) for row in rows]
        for entry in entries:
            entry["images"] = []
        if entries:
            entry_ids = [entry["id"] for entry in entries]
            placeholders = ",".join("?" for _ in entry_ids)
            images = db.execute(
                f"""SELECT id, nhat_ky_muc_id, filename, thumbnail_filename, ghi_chu
                    FROM nhat_ky_anh WHERE nhat_ky_muc_id IN ({placeholders})
                    ORDER BY id""",
                entry_ids,
            ).fetchall()
            by_entry = {entry_id: [] for entry_id in entry_ids}
            for image in images:
                by_entry[image["nhat_ky_muc_id"]].append({
                    "id": image["id"],
                    "url": f"/api/nhat-ky/images/{image['filename']}",
                    "thumbnail_url": (
                        f"/api/nhat-ky/thumbnails/{image['thumbnail_filename']}"
                        if image["thumbnail_filename"] else
                        f"/api/nhat-ky/images/{image['filename']}"
                    ),
                    "ghi_chu": image["ghi_chu"],
                })
            for entry in entries:
                entry["images"] = by_entry[entry["id"]]
        return entries


def entry_exists(database_path, entry_id):
    with closing(sqlite3.connect(database_path, timeout=10)) as db:
        return db.execute(
            "SELECT 1 FROM nhat_ky_muc WHERE id = ?", (entry_id,)
        ).fetchone() is not None


def count_entry_images(database_path, entry_id):
    with closing(sqlite3.connect(database_path, timeout=10)) as db:
        return db.execute(
            "SELECT COUNT(*) FROM nhat_ky_anh WHERE nhat_ky_muc_id = ?",
            (entry_id,),
        ).fetchone()[0]


def get_entry_image_by_upload_id(database_path, entry_id, upload_id):
    with closing(sqlite3.connect(database_path, timeout=10)) as db:
        db.row_factory = sqlite3.Row
        image = db.execute(
            """SELECT id, filename, thumbnail_filename, ghi_chu
               FROM nhat_ky_anh WHERE nhat_ky_muc_id = ? AND upload_id = ?""",
            (entry_id, upload_id),
        ).fetchone()
    if not image:
        return None
    return {
        "id": image["id"],
        "url": f"/api/nhat-ky/images/{image['filename']}",
        "thumbnail_url": (
            f"/api/nhat-ky/thumbnails/{image['thumbnail_filename']}"
            if image["thumbnail_filename"] else
            f"/api/nhat-ky/images/{image['filename']}"
        ),
        "ghi_chu": image["ghi_chu"],
    }


def add_entry_image(database_path, *, entry_id, filename, thumbnail_filename, upload_id, note):
    with closing(sqlite3.connect(database_path, timeout=10)) as db:
        cursor = db.execute(
            """INSERT INTO nhat_ky_anh
               (nhat_ky_muc_id, filename, thumbnail_filename, upload_id, ghi_chu)
               VALUES (?, ?, ?, ?, ?)""",
            (entry_id, filename, thumbnail_filename, upload_id, note),
        )
        image_id = cursor.lastrowid
        db.commit()
    return {
        "id": image_id,
        "url": f"/api/nhat-ky/images/{filename}",
        "thumbnail_url": f"/api/nhat-ky/thumbnails/{thumbnail_filename}",
        "ghi_chu": note,
    }


def get_daily_summary(database_path, project, diary_date):
    with closing(sqlite3.connect(database_path, timeout=10)) as db:
        db.row_factory = sqlite3.Row
        row = db.execute(
            "SELECT * FROM nhat_ky_ngay WHERE cong_trinh = ? AND ngay = ?",
            (project, diary_date),
        ).fetchone()
        if not row:
            return None
        summary = dict(row)
        summary["mua_ca_ngay"] = bool(summary.get("mua_ca_ngay", 0))
        return summary


def update_daily_summary(database_path, *, project, diary_date, user_id, workforce_count,
                         workforce_notes, equipment, weather, weather_notes, all_day_rain):
    with closing(sqlite3.connect(database_path, timeout=10)) as db:
        db.execute("PRAGMA foreign_keys = ON")
        day_id = _get_or_create_day(db, project, diary_date, user_id)
        db.execute(
            """UPDATE nhat_ky_ngay
               SET nhan_luc_so_nguoi = ?, nhan_luc_ghi_chu = ?, thiet_bi = ?,
                   thoi_tiet = ?, ghi_chu_thoi_tiet = ?, mua_ca_ngay = ?
               WHERE id = ?""",
            (workforce_count, workforce_notes, equipment, weather, weather_notes, int(all_day_rain), day_id),
        )
        db.commit()
    return get_daily_summary(database_path, project, diary_date)


def create_entry(database_path, *, project, diary_date, task_id, entry_time, description,

                 user_id, images=(), client_uid=None):
    with sqlite3.connect(database_path, timeout=10) as db:
        db.execute("PRAGMA foreign_keys = ON")
        if client_uid:
            db.row_factory = sqlite3.Row
            existing = db.execute("SELECT id FROM nhat_ky_muc WHERE client_uid = ?", (client_uid,)).fetchone()
            if existing:
                existing_id = existing["id"]
                return next((entry for entry in list_entries(database_path) if entry["id"] == existing_id), None)
        diary_id = _get_or_create_day(db, project, diary_date, user_id)
        cursor = db.execute(
            """INSERT INTO nhat_ky_muc
               (nhat_ky_ngay_id, cong_viec_id, gio, noi_dung, nguoi_lap_id, client_uid)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (diary_id, task_id, entry_time, description, user_id, client_uid),
                      )
        entry_id = cursor.lastrowid
        db.executemany(
            """INSERT INTO nhat_ky_anh (nhat_ky_muc_id, filename, ghi_chu)
               VALUES (?, ?, ?)""",
            [(entry_id, image["filename"], image["ghi_chu"]) for image in images],
        )
        db.commit()
    return next((entry for entry in list_entries(database_path, project=project, diary_date=diary_date) if entry["id"] == entry_id), None)


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


from app.extensions import db
from datetime import datetime


# Bảng lịch sử chuyển đổi đội thi công (S-25)
class LichSuPhanCong(db.Model):
    __tablename__ = 'lich_su_phan_cong'

    id = db.Column(db.Integer, primary_key=True)
    cong_viec_id = db.Column(
        db.Integer,
        db.ForeignKey('cong_viec.id'),
        nullable=False
    )
    doi_cu_id = db.Column(db.Integer, nullable=True)
    doi_moi_id = db.Column(db.Integer, nullable=False)
    nguoi_thuc_hien = db.Column(
        db.String(100),
        default="Chỉ huy trưởng"
    )
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# Bảng báo cáo khối lượng làm theo ngày (S-26)
class NhatKyKhoiLuong(db.Model):
    __tablename__ = 'nhat_ky_khoi_luong'

    id = db.Column(db.Integer, primary_key=True)
    cong_viec_id = db.Column(
        db.Integer,
        db.ForeignKey('cong_viec.id'),
        nullable=False
    )
    khoi_luong_ngay = db.Column(db.Float, nullable=False)
    nguoi_bao_cao = db.Column(
        db.String(100),
        default="Đội trưởng"
    )
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
