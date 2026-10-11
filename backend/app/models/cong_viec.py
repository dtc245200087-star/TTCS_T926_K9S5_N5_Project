import sqlite3
from contextlib import closing


INITIAL_TASKS = (
    (1, "Đổ bê tông móng", "Khu đô thị Bắc Sông Cầu", "Nguyễn Văn An", "Đang thực hiện", "2026-10-05"),
    (2, "Lắp đặt cốt thép", "Tòa nhà văn phòng A1", "Trần Minh Đức", "Hoàn thành", "2026-10-02"),
    (3, "Kiểm tra vật tư", "Nhà máy sản xuất B2", "Lê Hoàng Nam", "Chờ xử lý", "2026-10-04"),
)


def initialize_database(database_path):
    with closing(sqlite3.connect(database_path, timeout=10)) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS cong_viec (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ten TEXT NOT NULL,
            cong_trinh TEXT,
            nguoi_phu_trach TEXT,
            trang_thai TEXT,
            han TEXT,
            ngay_bat_dau_thuc_te TEXT,
            ngay_ket_thuc_thuc_te TEXT,
            phan_tram_hoan_thanh INTEGER NOT NULL DEFAULT 0
                CHECK (phan_tram_hoan_thanh BETWEEN 0 AND 100),
            CHECK (
                ngay_bat_dau_thuc_te IS NULL OR ngay_ket_thuc_thuc_te IS NULL
                OR ngay_ket_thuc_thuc_te >= ngay_bat_dau_thuc_te
            )
        )""")
        columns = {
            row[1] for row in db.execute("PRAGMA table_info(cong_viec)").fetchall()
        }
        migrations = (
            ("ngay_bat_dau_thuc_te", "TEXT"),
            ("ngay_ket_thuc_thuc_te", "TEXT"),
            ("phan_tram_hoan_thanh", "INTEGER NOT NULL DEFAULT 0 CHECK (phan_tram_hoan_thanh BETWEEN 0 AND 100)"),
        )
        for column, definition in migrations:
            if column not in columns:
                db.execute(f"ALTER TABLE cong_viec ADD COLUMN {column} {definition}")

        db.executescript("""
            CREATE TRIGGER IF NOT EXISTS cong_viec_actual_dates_insert
            BEFORE INSERT ON cong_viec
            WHEN NEW.ngay_bat_dau_thuc_te IS NOT NULL
                 AND NEW.ngay_ket_thuc_thuc_te IS NOT NULL
                 AND NEW.ngay_ket_thuc_thuc_te < NEW.ngay_bat_dau_thuc_te
            BEGIN
                SELECT RAISE(ABORT, 'actual_end_before_start');
            END;
            CREATE TRIGGER IF NOT EXISTS cong_viec_actual_dates_update
            BEFORE UPDATE OF ngay_bat_dau_thuc_te, ngay_ket_thuc_thuc_te ON cong_viec
            WHEN NEW.ngay_bat_dau_thuc_te IS NOT NULL
                 AND NEW.ngay_ket_thuc_thuc_te IS NOT NULL
                 AND NEW.ngay_ket_thuc_thuc_te < NEW.ngay_bat_dau_thuc_te
            BEGIN
                SELECT RAISE(ABORT, 'actual_end_before_start');
            END;
        """)
        if db.execute("SELECT COUNT(*) FROM cong_viec").fetchone()[0] == 0:
            db.executemany(
                """INSERT INTO cong_viec
                   (id, ten, cong_trinh, nguoi_phu_trach, trang_thai, han)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                INITIAL_TASKS,
            )
        db.commit()


def list_tasks(database_path):
    with closing(sqlite3.connect(database_path, timeout=10)) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute(
            """SELECT id, ten, cong_trinh, nguoi_phu_trach, trang_thai, han,
                      ngay_bat_dau_thuc_te, ngay_ket_thuc_thuc_te, phan_tram_hoan_thanh
               FROM cong_viec ORDER BY id"""
        ).fetchall()
        return [dict(row) for row in rows]


def update_actual_progress(database_path, task_id, start_date, end_date, completion):
    with closing(sqlite3.connect(database_path, timeout=10)) as db:
        cursor = db.execute(
            """UPDATE cong_viec
               SET ngay_bat_dau_thuc_te = ?, ngay_ket_thuc_thuc_te = ?,
                   phan_tram_hoan_thanh = ?
               WHERE id = ?""",
            (start_date, end_date, completion, task_id),
        )
        db.commit()
        return cursor.rowcount > 0