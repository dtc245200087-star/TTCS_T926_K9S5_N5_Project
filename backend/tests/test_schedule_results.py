import sqlite3
import tempfile
import unittest
from contextlib import closing
from unittest.mock import patch
from pathlib import Path

from app import create_app
from app.models.cong_viec import get_schedule_results, initialize_database


class ScheduleResultsTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = str(Path(self.temp_dir.name) / "schedule.db")
        self.env_patch = patch.dict(
            "os.environ",
            {"INITIAL_ADMIN_PASSWORD": "test-password-123"},
        )
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "USER_DATABASE": self.database,
        })
        self.client = self.app.test_client()
        with self.client.session_transaction() as session:
            session["user_id"] = 1
            session["csrf_token"] = "test-csrf"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_persists_early_and_late_times_and_delay(self):
        results, has_cycle = get_schedule_results(self.database)

        self.assertFalse(has_cycle)
        materials = next(row for row in results if row["ten"] == "Kiểm tra vật tư")
        self.assertEqual(
            (materials["es"], materials["ef"], materials["ls"], materials["lf"]),
            (2, 7, 13, 18),
        )
        self.assertEqual(materials["total_float"], 11)
        self.assertFalse(materials["is_critical"])

        with closing(sqlite3.connect(self.database)) as db:
            count = db.execute("SELECT COUNT(*) FROM schedule_results").fetchone()[0]
        self.assertEqual(count, len(results))

    def test_matches_every_k01_hand_calculated_schedule_value(self):
        results, has_cycle = get_schedule_results(self.database)

        self.assertFalse(has_cycle)
        actual = {
            row["ten"]: (
                row["es"],
                row["ef"],
                row["ls"],
                row["lf"],
                row["total_float"],
                bool(row["is_critical"]),
            )
            for row in results
        }
        expected = {
            "Chuẩn bị mặt bằng": (0, 2, 0, 2, 0, True),
            "Khảo sát và định vị công trình": (2, 3, 2, 3, 0, True),
            "Đào móng": (3, 6, 3, 6, 0, True),
            "Lắp đặt cốt thép": (6, 10, 6, 10, 0, True),
            "Đổ bê tông móng": (10, 12, 10, 12, 0, True),
            "Thi công kết cấu khung": (12, 17, 12, 17, 0, True),
            "Kiểm tra vật tư": (2, 7, 13, 18, 11, False),
            "Thi công hệ thống MEP âm": (17, 20, 17, 20, 0, True),
            "Lắp đặt cửa sổ": (17, 19, 18, 20, 1, False),
            "Hoàn thiện công trình": (20, 25, 20, 25, 0, True),
        }
        self.assertEqual(actual, expected)

    def test_calculates_all_four_relationship_types_and_uneven_parallel_branches(self):
        with closing(sqlite3.connect(self.database)) as db:
            db.execute("DELETE FROM cong_viec")
            db.executemany(
                """INSERT INTO cong_viec (id, ten, trang_thai, es, ef)
                   VALUES (?, ?, 'Chờ xử lý', ?, ?)""",
                [
                    (101, "Start", 4, 8),
                    (102, "SS branch", 0, 3),
                    (103, "FF branch", 0, 2),
                    (104, "SF branch", 0, 3),
                    (105, "Join", 0, 2),
                ],
            )
            db.executemany(
                """INSERT INTO task_dependencies
                   (task_id, depends_on_task_id, relationship_type)
                   VALUES (?, ?, ?)""",
                [
                    (102, 101, "SS"),
                    (103, 101, "FF"),
                    (104, 101, "SF"),
                    (105, 102, "FS"),
                    (105, 103, "FF"),
                ],
            )
            db.commit()

        results, has_cycle = get_schedule_results(self.database)

        self.assertFalse(has_cycle)
        actual = {
            row["ten"]: (
                row["es"],
                row["ef"],
                row["ls"],
                row["lf"],
                row["total_float"],
            )
            for row in results
        }
        self.assertEqual(actual, {
            "Start": (4, 8, 4, 8, 0),
            "SS branch": (4, 7, 4, 7, 0),
            "FF branch": (6, 8, 7, 9, 1),
            "SF branch": (1, 4, 6, 9, 5),
            "Join": (7, 9, 7, 9, 0),
        })

    def test_task_schedule_changes_mark_results_for_recalculation(self):
        with closing(sqlite3.connect(self.database)) as db:
            db.execute(
                "UPDATE cong_viec SET ef = ef + 2 WHERE ten = ?",
                ("Lắp đặt cốt thép",),
            )
            db.commit()

        results, has_cycle = get_schedule_results(self.database)

        self.assertFalse(has_cycle)
        concrete = next(row for row in results if row["ten"] == "Đổ bê tông móng")
        self.assertEqual((concrete["es"], concrete["ef"]), (12, 14))

    def test_migrates_legacy_dependency_column_and_preserves_edges(self):
        with closing(sqlite3.connect(self.database)) as db:
            task_ids = dict(db.execute("SELECT ten, id FROM cong_viec"))
            db.execute(
                "ALTER TABLE task_dependencies RENAME COLUMN depends_on_task_id TO depends_on_id"
            )
            db.execute(
                "INSERT INTO task_dependencies (task_id, depends_on_id) VALUES (?, ?)",
                (task_ids["Đổ bê tông móng"], task_ids["Kiểm tra vật tư"]),
            )
            db.commit()

        initialize_database(self.database)

        with closing(sqlite3.connect(self.database)) as db:
            columns = {
                row[1] for row in db.execute("PRAGMA table_info(task_dependencies)")
            }
            relation = db.execute(
                "SELECT task_id, depends_on_task_id, relationship_type "
                "FROM task_dependencies "
                "WHERE task_id = ? AND depends_on_task_id = ?",
                (
                    task_ids["Đổ bê tông móng"],
                    task_ids["Kiểm tra vật tư"],
                ),
            ).fetchone()
        self.assertIn("depends_on_task_id", columns)
        self.assertNotIn("depends_on_id", columns)
        self.assertEqual(
            relation,
            (
                task_ids["Đổ bê tông móng"],
                task_ids["Kiểm tra vật tư"],
                "FS",
            ),
        )
        _, has_cycle = get_schedule_results(self.database)
        self.assertFalse(has_cycle)

    def test_api_returns_tasks_and_schedule_results_together(self):
        response = self.client.get("/api/schedule-results")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("tasks", payload)
        self.assertIn("schedule_results", payload)
        self.assertFalse(payload["has_cycle"])
        self.assertTrue(payload["tasks"])
        self.assertTrue(payload["schedule_results"])

    def test_api_reports_cycles_instead_of_returning_stale_results(self):
        get_schedule_results(self.database)
        with closing(sqlite3.connect(self.database)) as db:
            task_ids = dict(db.execute("SELECT ten, id FROM cong_viec"))
            db.execute(
                "INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES (?, ?)",
                (task_ids["Chuẩn bị mặt bằng"], task_ids["Hoàn thiện công trình"]),
            )
            db.commit()

        response = self.client.get("/api/schedule-results")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["has_cycle"])
        self.assertEqual(payload["schedule_results"], [])
        self.assertTrue(payload["message"])

    def test_dependency_cycle_is_reported_without_discarding_last_results(self):
        previous_results, _ = get_schedule_results(self.database)
        with closing(sqlite3.connect(self.database)) as db:
            task_ids = dict(db.execute("SELECT ten, id FROM cong_viec"))
            db.execute(
                "INSERT INTO task_dependencies (task_id, depends_on_task_id) VALUES (?, ?)",
                (task_ids["Chuẩn bị mặt bằng"], task_ids["Hoàn thiện công trình"]),
            )
            db.commit()

        results, has_cycle = get_schedule_results(self.database)

        self.assertTrue(has_cycle)
        self.assertEqual(len(results), len(previous_results))


if __name__ == "__main__":
    unittest.main()
