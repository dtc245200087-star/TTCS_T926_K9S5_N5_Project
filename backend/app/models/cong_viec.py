import sqlite3
from collections import deque
from contextlib import closing

from app.extensions import db
from datetime import datetime

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    leader_id = db.Column(db.Integer, nullable=True) # ID Đội trưởng

class CongViec(db.Model):
    __tablename__ = 'cong_viec'
    id = db.Column(db.Integer, primary_key=True)
    ten_cong_viec = db.Column(db.String(200), nullable=False)
    tu_ngay = db.Column(db.DateTime, nullable=False)
    den_ngay = db.Column(db.DateTime, nullable=False)
    doi_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)

    @property
    def title(self):
        return self.ten_cong_viec

    @property
    def start_date(self):
        return self.tu_ngay

    @property
    def end_date(self):
        return self.den_ngay

    @property
    def team_id(self):
        return self.doi_id

    @team_id.setter
    def team_id(self, value):
        self.doi_id = value

Task = CongViec

class TaskHistory(db.Model):
    __tablename__ = 'task_history'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('cong_viec.id'), nullable=False)
    old_team_id = db.Column(db.Integer, nullable=True)
    new_team_id = db.Column(db.Integer, nullable=False)
    changed_by_user_id = db.Column(db.Integer, nullable=True) # ID Chỉ huy trưởng
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)


def get_schedule_results(database_path):
    with closing(sqlite3.connect(database_path, timeout=10)) as db:
        db.row_factory = sqlite3.Row
        db.execute("BEGIN IMMEDIATE")
        needs_recalculation = db.execute(
            "SELECT needs_recalculation FROM schedule_state WHERE id = 1"
        ).fetchone()[0]
        if needs_recalculation:
            scheduled_tasks = db.execute(
                """SELECT id, ten, cong_trinh, nguoi_phu_trach, trang_thai, es, ef
                   FROM cong_viec
                   WHERE es IS NOT NULL AND ef IS NOT NULL
                   ORDER BY id"""
            ).fetchall()
            task_by_id = {task["id"]: task for task in scheduled_tasks}
            predecessors = {task_id: [] for task_id in task_by_id}
            successors = {task_id: [] for task_id in task_by_id}
            dependencies = db.execute(
                "SELECT task_id, depends_on_id FROM task_dependencies"
            ).fetchall()
            for dependency in dependencies:
                task_id = dependency["task_id"]
                dependency_id = dependency["depends_on_id"]
                if task_id in task_by_id and dependency_id in task_by_id:
                    predecessors[task_id].append(dependency_id)
                    successors[dependency_id].append(task_id)

            indegree = {
                task_id: len(task_predecessors)
                for task_id, task_predecessors in predecessors.items()
            }
            queue = deque(
                task_id for task_id, degree in indegree.items() if degree == 0
            )
            order = []
            while queue:
                task_id = queue.popleft()
                order.append(task_id)
                for successor_id in successors[task_id]:
                    indegree[successor_id] -= 1
                    if indegree[successor_id] == 0:
                        queue.append(successor_id)

            if len(order) != len(task_by_id):
                results = db.execute(
                    """SELECT sr.task_id, cv.ten, cv.cong_trinh, cv.nguoi_phu_trach,
                              cv.trang_thai, sr.es, sr.ef, sr.ls, sr.lf,
                              sr.total_float, sr.is_critical
                       FROM schedule_results AS sr
                       JOIN cong_viec AS cv ON cv.id = sr.task_id
                       ORDER BY sr.es, sr.task_id"""
                ).fetchall()
                db.commit()
                return [dict(row) for row in results], True

            early_start = {}
            early_finish = {}
            for task_id in order:
                task = task_by_id[task_id]
                dependency_finish = max(
                    (early_finish[item] for item in predecessors[task_id]),
                    default=task["es"],
                )
                early_start[task_id] = max(task["es"], dependency_finish)
                duration = max(0, task["ef"] - task["es"])
                early_finish[task_id] = early_start[task_id] + duration

            project_finish = max(early_finish.values(), default=0)
            late_start = {}
            late_finish = {}
            for task_id in reversed(order):
                task = task_by_id[task_id]
                late_finish[task_id] = min(
                    (late_start[item] for item in successors[task_id]),
                    default=project_finish,
                )
                duration = max(0, task["ef"] - task["es"])
                late_start[task_id] = late_finish[task_id] - duration

            db.execute("DELETE FROM schedule_results")
            db.executemany(
                """INSERT INTO schedule_results
                   (task_id, es, ef, ls, lf, total_float, is_critical)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    (
                        task_id,
                        early_start[task_id],
                        early_finish[task_id],
                        late_start[task_id],
                        late_finish[task_id],
                        late_start[task_id] - early_start[task_id],
                        int(late_start[task_id] == early_start[task_id]),
                    )
                    for task_id in order
                ),
            )
            db.execute(
                "UPDATE schedule_state SET needs_recalculation = 0 WHERE id = 1"
            )

        results = db.execute(
            """SELECT sr.task_id, cv.ten, cv.cong_trinh, cv.nguoi_phu_trach,
                      cv.trang_thai, sr.es, sr.ef, sr.ls, sr.lf,
                      sr.total_float, sr.is_critical
               FROM schedule_results AS sr
               JOIN cong_viec AS cv ON cv.id = sr.task_id
               ORDER BY sr.es, sr.task_id"""
        ).fetchall()
        db.commit()
        return [dict(row) for row in results], False


INITIAL_TASKS = (
    (1, "Đổ bê tông móng", "Khu đô thị Bắc Sông Cầu", "Nguyễn Văn An", "Đang thực hiện", "2026-10-05"),
    (2, "Lắp đặt cốt thép", "Tòa nhà văn phòng A1", "Trần Minh Đức", "Hoàn thành", "2026-10-02"),
    (3, "Kiểm tra vật tư", "Nhà máy sản xuất B2", "Lê Hoàng Nam", "Chờ xử lý", "2026-10-04"),
)

SCHEDULE_TASKS = (
    ("Chuẩn bị mặt bằng", 0, 2, 0, 2, 0, 1),
    ("Khảo sát và định vị công trình", 2, 3, 2, 3, 0, 1),
    ("Đào móng", 3, 6, 3, 6, 0, 1),
    ("Lắp đặt cốt thép", 6, 10, 6, 10, 0, 1),
    ("Đổ bê tông móng", 10, 12, 10, 12, 0, 1),
    ("Thi công kết cấu khung", 12, 17, 12, 17, 0, 1),
    ("Kiểm tra vật tư", 2, 7, 13, 18, 11, 0),
    ("Thi công hệ thống MEP âm", 17, 20, 17, 20, 0, 1),
    ("Lắp đặt cửa sổ", 17, 19, 18, 20, 1, 0),
    ("Hoàn thiện công trình", 20, 25, 20, 25, 0, 1),
)

SCHEDULE_DEPENDENCIES = (
    ("Khảo sát và định vị công trình", "Chuẩn bị mặt bằng"),
    ("Đào móng", "Khảo sát và định vị công trình"),
    ("Lắp đặt cốt thép", "Đào móng"),
    ("Đổ bê tông móng", "Lắp đặt cốt thép"),
    ("Thi công kết cấu khung", "Đổ bê tông móng"),
    ("Thi công hệ thống MEP âm", "Thi công kết cấu khung"),
    ("Lắp đặt cửa sổ", "Thi công kết cấu khung"),
    ("Lắp đặt cửa sổ", "Kiểm tra vật tư"),
    ("Hoàn thiện công trình", "Thi công hệ thống MEP âm"),
    ("Hoàn thiện công trình", "Lắp đặt cửa sổ"),
)


def initialize_database(database_path):
    with closing(sqlite3.connect(database_path, timeout=10)) as db:
        db.execute("PRAGMA foreign_keys = ON")
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
            es INTEGER,
            ef INTEGER,
            ls INTEGER,
            lf INTEGER,
            total_float INTEGER,
            is_critical INTEGER,
            CHECK (
                ngay_bat_dau_thuc_te IS NULL OR ngay_ket_thuc_thuc_te IS NULL
                OR ngay_ket_thuc_thuc_te >= ngay_bat_dau_thuc_te
            )
        )""")
        db.executescript("""
            CREATE TABLE IF NOT EXISTS task_dependencies (
                task_id INTEGER NOT NULL,
                depends_on_id INTEGER NOT NULL,
                PRIMARY KEY (task_id, depends_on_id),
                CHECK (task_id != depends_on_id)
            );
            CREATE TABLE IF NOT EXISTS schedule_results (
                task_id INTEGER PRIMARY KEY,
                es INTEGER NOT NULL,
                ef INTEGER NOT NULL,
                ls INTEGER NOT NULL,
                lf INTEGER NOT NULL,
                total_float INTEGER NOT NULL,
                is_critical INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS schedule_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                needs_recalculation INTEGER NOT NULL DEFAULT 1,
                dependencies_seeded INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS baselines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                captured_by TEXT NOT NULL,
                captured_at TEXT NOT NULL,
                is_current INTEGER NOT NULL DEFAULT 1
                    CHECK (is_current IN (0, 1))
            );
            CREATE UNIQUE INDEX IF NOT EXISTS idx_baselines_single_current
                ON baselines (is_current) WHERE is_current = 1;
            CREATE TABLE IF NOT EXISTS baseline_details (
                baseline_id INTEGER NOT NULL
                    REFERENCES baselines(id) ON DELETE CASCADE,
                task_id INTEGER NOT NULL,
                ten TEXT NOT NULL,
                es INTEGER NOT NULL,
                ef INTEGER NOT NULL,
                ls INTEGER NOT NULL,
                lf INTEGER NOT NULL,
                PRIMARY KEY (baseline_id, task_id)
            );
            INSERT OR IGNORE INTO schedule_state (id, needs_recalculation)
            VALUES (1, 1);
            CREATE TRIGGER IF NOT EXISTS schedule_tasks_insert
            AFTER INSERT ON cong_viec
            BEGIN
                UPDATE schedule_state SET needs_recalculation = 1 WHERE id = 1;
            END;
            CREATE TRIGGER IF NOT EXISTS schedule_tasks_delete
            AFTER DELETE ON cong_viec
            BEGIN
                DELETE FROM task_dependencies
                WHERE task_id = OLD.id OR depends_on_id = OLD.id;
                DELETE FROM schedule_results WHERE task_id = OLD.id;
                UPDATE schedule_state SET needs_recalculation = 1 WHERE id = 1;
            END;
            CREATE TRIGGER IF NOT EXISTS schedule_tasks_update
            AFTER UPDATE OF ten, cong_trinh, nguoi_phu_trach, trang_thai, es, ef ON cong_viec
            BEGIN
                UPDATE schedule_state SET needs_recalculation = 1 WHERE id = 1;
            END;
            CREATE TRIGGER IF NOT EXISTS schedule_dependencies_insert
            AFTER INSERT ON task_dependencies
            BEGIN
                UPDATE schedule_state SET needs_recalculation = 1 WHERE id = 1;
            END;
            CREATE TRIGGER IF NOT EXISTS schedule_dependencies_delete
            AFTER DELETE ON task_dependencies
            BEGIN
                UPDATE schedule_state SET needs_recalculation = 1 WHERE id = 1;
            END;
            CREATE TRIGGER IF NOT EXISTS schedule_dependencies_update
            AFTER UPDATE ON task_dependencies
            BEGIN
                UPDATE schedule_state SET needs_recalculation = 1 WHERE id = 1;
            END;
        """)
        columns = {
            row[1] for row in db.execute("PRAGMA table_info(cong_viec)").fetchall()
        }
        migrations = (
            ("ngay_bat_dau_thuc_te", "TEXT"),
            ("ngay_ket_thuc_thuc_te", "TEXT"),
            ("phan_tram_hoan_thanh", "INTEGER NOT NULL DEFAULT 0 CHECK (phan_tram_hoan_thanh BETWEEN 0 AND 100)"),
            ("es", "INTEGER"),
            ("ef", "INTEGER"),
            ("ls", "INTEGER"),
            ("lf", "INTEGER"),
            ("total_float", "INTEGER"),
            ("is_critical", "INTEGER"),
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
        for task_name, es, ef, ls, lf, total_float, is_critical in SCHEDULE_TASKS:
            db.execute(
                """INSERT INTO cong_viec
                   (ten, trang_thai, es, ef, ls, lf, total_float, is_critical)
                   SELECT ?, 'Chờ xử lý', ?, ?, ?, ?, ?, ?
                   WHERE NOT EXISTS (
                       SELECT 1 FROM cong_viec WHERE ten = ?
                   )""",
                (task_name, es, ef, ls, lf, total_float, is_critical, task_name),
            )
            db.execute(
                """UPDATE cong_viec
                   SET es = ?, ef = ?, ls = ?, lf = ?, total_float = ?, is_critical = ?
                   WHERE ten = ? AND es IS NULL""",
                (es, ef, ls, lf, total_float, is_critical, task_name),
            )
        dependency_seeded = db.execute(
            "SELECT dependencies_seeded FROM schedule_state WHERE id = 1"
        ).fetchone()[0]
        if not dependency_seeded:
            task_ids = {
                name: task_id
                for task_id, name in db.execute(
                    "SELECT id, ten FROM cong_viec WHERE es IS NOT NULL AND ef IS NOT NULL"
                )
            }
            db.executemany(
                """INSERT OR IGNORE INTO task_dependencies (task_id, depends_on_id)
                   VALUES (?, ?)""",
                (
                    (task_ids[task_name], task_ids[dependency_name])
                    for task_name, dependency_name in SCHEDULE_DEPENDENCIES
                    if task_name in task_ids and dependency_name in task_ids
                ),
            )
            db.execute(
                "UPDATE schedule_state SET dependencies_seeded = 1 WHERE id = 1"
            )
        db.commit()


def list_tasks(database_path):
    with closing(sqlite3.connect(database_path, timeout=10)) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute(
            """SELECT id, ten, cong_trinh, nguoi_phu_trach, trang_thai, han,
                      ngay_bat_dau_thuc_te, ngay_ket_thuc_thuc_te,
                      phan_tram_hoan_thanh, es, ef, ls, lf, total_float, is_critical
               FROM cong_viec ORDER BY id"""
        ).fetchall()
        return [dict(row) for row in rows]


def update_actual_progress(
    database_path,
    task_id,
    start_date,
    end_date,
    completion,
    *,
    category_id=None,
    update_category=False,
):
    with closing(sqlite3.connect(database_path, timeout=10)) as db:
        cursor = db.execute(
            """UPDATE cong_viec
               SET ngay_bat_dau_thuc_te = ?, ngay_ket_thuc_thuc_te = ?,
                   phan_tram_hoan_thanh = ?
               WHERE id = ?""",
            (start_date, end_date, completion, task_id),
        )
        if cursor.rowcount:
            if update_category:
                db.execute(
                    "UPDATE cong_viec SET category_id = ? WHERE id = ?",
                    (category_id, task_id),
                )
                db.execute("DELETE FROM category_tasks WHERE task_id = ?", (task_id,))
                if category_id is not None:
                    db.execute(
                        "INSERT INTO category_tasks (category_id, task_id) VALUES (?, ?)",
                        (category_id, task_id),
                    )
        db.commit()
        return cursor.rowcount > 0