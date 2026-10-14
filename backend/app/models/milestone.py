import sqlite3
from contextlib import closing
from datetime import date, timedelta


def connect(database_path):
    db = sqlite3.connect(database_path, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def initialize_database(database_path):
    with closing(connect(database_path)) as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                parent_id INTEGER REFERENCES categories(id) ON DELETE RESTRICT,
                planned_start_date TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS category_tasks (
                task_id INTEGER PRIMARY KEY REFERENCES cong_viec(id) ON DELETE CASCADE,
                category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS task_dependencies (
                task_id INTEGER NOT NULL REFERENCES cong_viec(id) ON DELETE CASCADE,
                depends_on_task_id INTEGER NOT NULL REFERENCES cong_viec(id) ON DELETE CASCADE,
                PRIMARY KEY (task_id, depends_on_task_id),
                CHECK (task_id != depends_on_task_id)
            );
            CREATE TABLE IF NOT EXISTS milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL UNIQUE REFERENCES categories(id) ON DELETE CASCADE,
                deadline TEXT NOT NULL,
                created_by INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT
            );
            CREATE INDEX IF NOT EXISTS idx_categories_parent ON categories(parent_id);
            CREATE INDEX IF NOT EXISTS idx_category_tasks_category ON category_tasks(category_id);
            CREATE INDEX IF NOT EXISTS idx_task_dependencies_predecessor
                ON task_dependencies(depends_on_task_id);
            CREATE TRIGGER IF NOT EXISTS category_task_remove_dependencies
            AFTER DELETE ON category_tasks
            BEGIN
                DELETE FROM task_dependencies
                WHERE task_id = OLD.task_id OR depends_on_task_id = OLD.task_id;
            END;
        """)
        task_columns = {
            row["name"] for row in db.execute("PRAGMA table_info(cong_viec)").fetchall()
        }
        if "category_id" not in task_columns:
            db.execute(
                "ALTER TABLE cong_viec ADD COLUMN category_id INTEGER "
                "REFERENCES categories(id) ON DELETE SET NULL"
            )
        db.execute(
            """UPDATE cong_viec
               SET category_id = (
                   SELECT category_id FROM category_tasks
                   WHERE category_tasks.task_id = cong_viec.id
               )
               WHERE category_id IS NULL AND EXISTS (
                   SELECT 1 FROM category_tasks
                   WHERE category_tasks.task_id = cong_viec.id
               )"""
        )
        db.commit()
        db.commit()


def _valid_date(value):
    try:
        return isinstance(value, str) and date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def _row_dict(row):
    return dict(row) if row else None


def list_categories(database_path):
    with closing(connect(database_path)) as db:
        categories = db.execute(
            "SELECT id, name, parent_id, planned_start_date FROM categories ORDER BY name, id"
        ).fetchall()
        tasks = db.execute(
            """SELECT cv.category_id, cv.id, cv.ten, cv.es, cv.ef
               FROM cong_viec cv
               WHERE cv.category_id IS NOT NULL
               ORDER BY cv.ten, cv.id"""
        ).fetchall()
        dependencies = db.execute(
            """SELECT td.task_id, td.depends_on_task_id
               FROM task_dependencies td
               ORDER BY td.task_id, td.depends_on_task_id"""
        ).fetchall()
        milestones = {
            row["category_id"]: dict(row)
            for row in db.execute(
                "SELECT id, category_id, deadline FROM milestones"
            ).fetchall()
        }

    nodes = {
        row["id"]: {
            **dict(row),
            "tasks": [],
            "dependencies": [],
            "milestone": milestones.get(row["id"]),
            "children": [],
        }
        for row in categories
    }
    for task in tasks:
        nodes[task["category_id"]]["tasks"].append({
            "id": task["id"],
            "task_name": task["ten"],
            "es": task["es"],
            "ef": task["ef"],
        })
    for relation in dependencies:
        for category_id, node in nodes.items():
            if any(task["id"] == relation["task_id"] for task in node["tasks"]):
                node["dependencies"].append({
                    "task_id": relation["task_id"],
                    "depends_on_task_id": relation["depends_on_task_id"],
                })
                break
    roots = []
    for node in nodes.values():
        parent = nodes.get(node["parent_id"])
        if parent:
            parent["children"].append(node)
        else:
            roots.append(node)
    return roots


def list_unassigned_tasks(database_path):
    with closing(connect(database_path)) as db:
        rows = db.execute(
            """SELECT cv.id, cv.ten AS task_name, cv.es, cv.ef
               FROM cong_viec cv
               WHERE cv.category_id IS NULL
               ORDER BY cv.ten, cv.id"""
        ).fetchall()
        return [dict(row) for row in rows]


def get_category(database_path, category_id):
    with closing(connect(database_path)) as db:
        return _row_dict(db.execute(
            "SELECT id, name, parent_id, planned_start_date FROM categories WHERE id = ?",
            (category_id,),
        ).fetchone())


def create_category(database_path, name, parent_id, planned_start_date):
    if not _valid_date(planned_start_date):
        raise ValueError("Ngày bắt đầu kế hoạch phải theo định dạng YYYY-MM-DD.")
    with closing(connect(database_path)) as db:
        cursor = db.execute(
            """INSERT INTO categories (name, parent_id, planned_start_date)
               VALUES (?, ?, ?)""",
            (name, parent_id, planned_start_date),
        )
        db.commit()
        return _row_dict(db.execute(
            "SELECT id, name, parent_id, planned_start_date FROM categories WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone())


def update_category(database_path, category_id, *, name=None, parent_id=None, planned_start_date=None):
    fields, values = [], []
    if name is not None:
        fields.append("name = ?")
        values.append(name)
    if parent_id is not None:
        if parent_id == category_id:
            raise ValueError("Hạng mục không thể là hạng mục cha của chính nó.")
        with closing(connect(database_path)) as db:
            descendants = db.execute(
                """WITH RECURSIVE subtree(id) AS (
                       SELECT id FROM categories WHERE parent_id = ?
                       UNION ALL
                       SELECT child.id FROM categories child JOIN subtree parent
                         ON child.parent_id = parent.id
                   )
                   SELECT id FROM subtree""",
                (category_id,),
            ).fetchall()
            if parent_id in {row["id"] for row in descendants}:
                raise ValueError("Không thể chuyển hạng mục xuống bên dưới chính nó.")
        fields.append("parent_id = ?")
        values.append(parent_id)
    if planned_start_date is not None:
        if not _valid_date(planned_start_date):
            raise ValueError("Ngày bắt đầu kế hoạch phải theo định dạng YYYY-MM-DD.")
        fields.append("planned_start_date = ?")
        values.append(planned_start_date)
    if fields:
        values.append(category_id)
        with closing(connect(database_path)) as db:
            db.execute(f"UPDATE categories SET {', '.join(fields)} WHERE id = ?", values)
            db.commit()
    return get_category(database_path, category_id)


def delete_category(database_path, category_id):
    with closing(connect(database_path)) as db:
        cursor = db.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        db.commit()
        return cursor.rowcount > 0


def assign_task(database_path, category_id, task_id):
    with closing(connect(database_path)) as db:
        cursor = db.execute(
            "UPDATE cong_viec SET category_id = ? WHERE id = ? AND category_id IS NULL",
            (category_id, task_id),
        )
        if cursor.rowcount == 0:
            raise sqlite3.IntegrityError("task_missing_or_already_assigned")
        db.execute(
            "INSERT INTO category_tasks (category_id, task_id) VALUES (?, ?)",
            (category_id, task_id),
        )
        db.commit()


def unassign_task(database_path, task_id):
    with closing(connect(database_path)) as db:
        cursor = db.execute(
            "UPDATE cong_viec SET category_id = NULL WHERE id = ? AND category_id IS NOT NULL",
            (task_id,),
        )
        db.execute("DELETE FROM category_tasks WHERE task_id = ?", (task_id,))
        db.commit()
        return cursor.rowcount > 0


def list_dependencies(database_path, category_id):
    with closing(connect(database_path)) as db:
        rows = db.execute(
            """SELECT td.task_id, td.depends_on_task_id
               FROM task_dependencies td
               JOIN category_tasks current ON current.task_id = td.task_id
               WHERE current.category_id = ?
               ORDER BY td.task_id, td.depends_on_task_id""",
            (category_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def add_dependency(database_path, task_id, depends_on_task_id):
    if task_id == depends_on_task_id:
        raise ValueError("Công việc không thể phụ thuộc vào chính nó.")
    with closing(connect(database_path)) as db:
        assigned = db.execute(
            """SELECT task_id, category_id FROM category_tasks
               WHERE task_id IN (?, ?)""",
            (task_id, depends_on_task_id),
        ).fetchall()
        if len(assigned) != 2 or assigned[0]["category_id"] != assigned[1]["category_id"]:
            raise ValueError("Hai công việc phải cùng thuộc một hạng mục.")

        edges = db.execute(
            "SELECT task_id, depends_on_task_id FROM task_dependencies"
        ).fetchall()
        successors = {}
        for edge in edges:
            successors.setdefault(edge["depends_on_task_id"], set()).add(edge["task_id"])

        pending, visited = [task_id], set()
        while pending:
            current = pending.pop()
            if current == depends_on_task_id:
                raise ValueError("Quan hệ này tạo thành vòng lặp phụ thuộc.")
            if current not in visited:
                visited.add(current)
                pending.extend(successors.get(current, ()))

        db.execute(
            "INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES (?, ?)",
            (task_id, depends_on_task_id),
        )
        db.commit()


def remove_dependency(database_path, task_id, depends_on_task_id):
    with closing(connect(database_path)) as db:
        cursor = db.execute(
            """DELETE FROM task_dependencies
               WHERE task_id = ? AND depends_on_task_id = ?""",
            (task_id, depends_on_task_id),
        )
        db.commit()
        return cursor.rowcount > 0


def _category_scope(db, category_id):
    return db.execute(
        """WITH RECURSIVE subtree(id) AS (
               SELECT id FROM categories WHERE id = ?
               UNION ALL
               SELECT child.id FROM categories child JOIN subtree parent
                 ON child.parent_id = parent.id
           )
           SELECT id FROM subtree""",
        (category_id,),
    ).fetchall()


def calculate_milestone(database_path, category_id, deadline):
    if not _valid_date(deadline):
        raise ValueError("Ngày bàn giao phải theo định dạng YYYY-MM-DD.")
    with closing(connect(database_path)) as db:
        category = db.execute(
            "SELECT id, name, planned_start_date FROM categories WHERE id = ?",
            (category_id,),
        ).fetchone()
        if not category:
            return None

        category_ids = [row["id"] for row in _category_scope(db, category_id)]
        placeholders = ",".join("?" for _ in category_ids)
        task_rows = db.execute(
            f"""SELECT cv.id, cv.ten, cv.es, cv.ef
                FROM category_tasks ct
                JOIN cong_viec cv ON cv.id = ct.task_id
                WHERE ct.category_id IN ({placeholders})
                  AND cv.es IS NOT NULL AND cv.ef IS NOT NULL
                  AND cv.ef >= cv.es
                ORDER BY cv.id""",
            category_ids,
        ).fetchall()
        tasks = {row["id"]: row for row in task_rows}
        if not tasks:
            return {
                "category_id": category_id,
                "category_name": category["name"],
                "deadline": deadline,
                "projected_finish": None,
                "overrun_days": 0,
                "delay_chain": [],
            }

        task_ids = list(tasks)
        task_placeholders = ",".join("?" for _ in task_ids)
        dependencies = db.execute(
            f"""SELECT task_id, depends_on_task_id FROM task_dependencies
                WHERE task_id IN ({task_placeholders})
                  AND depends_on_task_id IN ({task_placeholders})""",
            task_ids + task_ids,
        ).fetchall()
        predecessors = {task_id: [] for task_id in tasks}
        successors = {task_id: [] for task_id in tasks}
        for relation in dependencies:
            task_id = relation["task_id"]
            predecessor_id = relation["depends_on_task_id"]
            if task_id in tasks and predecessor_id in tasks:
                predecessors[task_id].append(predecessor_id)
                successors[predecessor_id].append(task_id)

        remaining = {task_id: len(items) for task_id, items in predecessors.items()}
        ready = sorted(task_id for task_id, count in remaining.items() if count == 0)
        finish_offsets, paths = {}, {}
        while ready:
            task_id = ready.pop(0)
            duration = tasks[task_id]["ef"] - tasks[task_id]["es"]
            predecessor_id = max(
                predecessors[task_id],
                key=lambda item: (finish_offsets[item], -item),
                default=None,
            )
            dependency_finish = (
                finish_offsets[predecessor_id] + duration
                if predecessor_id is not None else 0
            )
            finish_offsets[task_id] = max(tasks[task_id]["ef"], dependency_finish)
            paths[task_id] = (
                paths[predecessor_id] if predecessor_id is not None else []
            ) + [task_id]
            for successor_id in successors[task_id]:
                remaining[successor_id] -= 1
                if remaining[successor_id] == 0:
                    ready.append(successor_id)
            ready.sort()

        if len(finish_offsets) != len(tasks):
            raise ValueError("Phát hiện vòng lặp trong quan hệ phụ thuộc công việc.")
        terminal_tasks = [task_id for task_id in tasks if not successors[task_id]]
        final_task_id = max(
            terminal_tasks,
            key=lambda item: (finish_offsets[item], -item),
        )
        projected_finish = (
            date.fromisoformat(category["planned_start_date"])
            + timedelta(days=finish_offsets[final_task_id])
        )
        due_date = date.fromisoformat(deadline)
        overrun_days = max((projected_finish - due_date).days, 0)
        return {
            "category_id": category_id,
            "category_name": category["name"],
            "deadline": deadline,
            "projected_finish": projected_finish.isoformat(),
            "overrun_days": overrun_days,
            "delay_chain": [tasks[task_id]["ten"] for task_id in paths[final_task_id]],
        }


def list_milestones(database_path):
    with closing(connect(database_path)) as db:
        rows = db.execute(
            """SELECT m.id, m.category_id, c.name AS category_name, m.deadline,
                      m.created_by, u.full_name AS created_by_name
               FROM milestones m
               JOIN categories c ON c.id = m.category_id
               JOIN users u ON u.id = m.created_by
               ORDER BY m.deadline, m.id"""
        ).fetchall()
        return [dict(row) for row in rows]


def get_milestone(database_path, milestone_id):
    with closing(connect(database_path)) as db:
        row = db.execute(
            """SELECT m.id, m.category_id, c.name AS category_name, m.deadline,
                      m.created_by, u.full_name AS created_by_name
               FROM milestones m
               JOIN categories c ON c.id = m.category_id
               JOIN users u ON u.id = m.created_by
               WHERE m.id = ?""",
            (milestone_id,),
        ).fetchone()
        return _row_dict(row)


def get_milestone_for_category(database_path, category_id):
    with closing(connect(database_path)) as db:
        row = db.execute(
            """SELECT m.id, m.category_id, c.name AS category_name, m.deadline,
                      m.created_by, u.full_name AS created_by_name
               FROM milestones m
               JOIN categories c ON c.id = m.category_id
               JOIN users u ON u.id = m.created_by
               WHERE m.category_id = ?""",
            (category_id,),
        ).fetchone()
        return _row_dict(row)


def create_milestone(database_path, category_id, deadline, created_by):
    if not _valid_date(deadline):
        raise ValueError("Ngày bàn giao phải theo định dạng YYYY-MM-DD.")
    with closing(connect(database_path)) as db:
        cursor = db.execute(
            """INSERT INTO milestones (category_id, deadline, created_by)
               VALUES (?, ?, ?)""",
            (category_id, deadline, created_by),
        )
        db.commit()
        milestone_id = cursor.lastrowid
    return get_milestone(database_path, milestone_id)


def update_milestone(database_path, milestone_id, *, category_id=None, deadline=None):
    if deadline is not None and not _valid_date(deadline):
        raise ValueError("Ngày bàn giao phải theo định dạng YYYY-MM-DD.")
    fields, values = [], []
    if category_id is not None:
        fields.append("category_id = ?")
        values.append(category_id)
    if deadline is not None:
        fields.append("deadline = ?")
        values.append(deadline)
    if fields:
        values.append(milestone_id)
        with closing(connect(database_path)) as db:
            db.execute(f"UPDATE milestones SET {', '.join(fields)} WHERE id = ?", values)
            db.commit()
    return get_milestone(database_path, milestone_id)


def delete_milestone(database_path, milestone_id):
    with closing(connect(database_path)) as db:
        cursor = db.execute("DELETE FROM milestones WHERE id = ?", (milestone_id,))
        db.commit()
        return cursor.rowcount > 0


def list_alerts(database_path):
    alerts = []
    for milestone in list_milestones(database_path):
        forecast = calculate_milestone(
            database_path, milestone["category_id"], milestone["deadline"]
        )
        if forecast and forecast["overrun_days"] > 0:
            alerts.append({
                "id": milestone["id"],
                **forecast,
            })
    return alerts


def get_alert(database_path, milestone_id):
    milestone = get_milestone(database_path, milestone_id)
    if not milestone:
        return None
    forecast = calculate_milestone(
        database_path, milestone["category_id"], milestone["deadline"]
    )
    return {"id": milestone_id, **forecast}
