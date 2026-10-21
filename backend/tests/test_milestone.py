import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import create_app
from app.models import cong_viec, milestone, user


class MilestoneModelTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = str(Path(self.temp_dir.name) / "test.db")
        user.initialize_database(self.database_path)
        cong_viec.initialize_database(self.database_path)
        milestone.initialize_database(self.database_path)
        self.tasks = {
            task["ten"]: task["id"]
            for task in cong_viec.list_tasks(self.database_path)
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_forecast_returns_overrun_and_names_only_for_the_longest_chain(self):
        category = milestone.create_category(
            self.database_path, "Móng", None, "2026-10-01"
        )
        first = self.tasks["Chuẩn bị mặt bằng"]
        second = self.tasks["Kiểm tra vật tư"]
        milestone.assign_task(self.database_path, category["id"], first)
        milestone.assign_task(self.database_path, category["id"], second)
        milestone.add_dependency(self.database_path, second, first)

        forecast = milestone.calculate_milestone(
            self.database_path, category["id"], "2026-10-02"
        )

        self.assertEqual(forecast["projected_finish"], "2026-10-08")
        self.assertEqual(forecast["overrun_days"], 6)
        self.assertEqual(
            forecast["delay_chain"],
            ["Chuẩn bị mặt bằng", "Kiểm tra vật tư"],
        )
        self.assertTrue(all(isinstance(task_name, str) for task_name in forecast["delay_chain"]))

    def test_dependency_cycle_is_rejected(self):
        category = milestone.create_category(
            self.database_path, "Kết cấu", None, "2026-10-01"
        )
        first = self.tasks["Chuẩn bị mặt bằng"]
        second = self.tasks["Kiểm tra vật tư"]
        milestone.assign_task(self.database_path, category["id"], first)
        milestone.assign_task(self.database_path, category["id"], second)
        milestone.add_dependency(self.database_path, second, first)

        with self.assertRaisesRegex(milestone.DependencyCycleError, "vòng phụ thuộc"):
            milestone.add_dependency(self.database_path, first, second)
        self.assertEqual(
            milestone.list_dependencies(self.database_path, category["id"]),
            [{
                "task_id": second,
                "depends_on_task_id": first,
                "relationship_type": "FS",
            }],
        )

    def test_alert_query_only_returns_milestones_past_deadline(self):
        user_id = user.create_user(
            self.database_path, "admin", "Admin", "test-password", "admin"
        )["id"]
        late_category = milestone.create_category(
            self.database_path, "Móng", None, "2026-10-01"
        )
        on_time_category = milestone.create_category(
            self.database_path, "Hoàn thiện", None, "2026-10-01"
        )
        milestone.assign_task(
            self.database_path, late_category["id"], self.tasks["Chuẩn bị mặt bằng"]
        )
        milestone.assign_task(
            self.database_path, on_time_category["id"], self.tasks["Đào móng"]
        )
        late = milestone.create_milestone(
            self.database_path, late_category["id"], "2026-10-02", user_id
        )
        milestone.create_milestone(
            self.database_path, on_time_category["id"], "2026-10-07", user_id
        )

        alerts = milestone.list_alerts(self.database_path)
        detail = milestone.get_alert(self.database_path, late["id"])

        self.assertEqual([alert["id"] for alert in alerts], [late["id"]])
        self.assertEqual(detail["overrun_days"], 1)
        self.assertNotIn("task_id", detail)
        self.assertNotIn("task_ids", detail)

    def test_assigning_and_unassigning_task_updates_category_id(self):
        category = milestone.create_category(
            self.database_path, "Móng", None, "2026-10-01"
        )
        task_id = self.tasks["Chuẩn bị mặt bằng"]

        milestone.assign_task(self.database_path, category["id"], task_id)
        assigned_task = next(
            task for task in cong_viec.list_tasks(self.database_path)
            if task["id"] == task_id
        )
        self.assertEqual(assigned_task["category_id"], category["id"])
        self.assertEqual(milestone.list_categories(self.database_path)[0]["tasks"][0]["id"], task_id)

        self.assertTrue(milestone.unassign_task(self.database_path, task_id))
        unassigned_task = next(
            task for task in cong_viec.list_tasks(self.database_path)
            if task["id"] == task_id
        )
        self.assertIsNone(unassigned_task["category_id"])
        self.assertIn(
            task_id,
            [task["id"] for task in milestone.list_unassigned_tasks(self.database_path)],
        )


class MilestoneAuthorizationTests(unittest.TestCase):
    def test_dependency_api_persists_selected_relationship_type(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = str(Path(temp_dir) / "users.db")
            with patch.dict(os.environ, {
                "INITIAL_ADMIN_USERNAME": "admin",
                "INITIAL_ADMIN_PASSWORD": "test-admin-password",
            }):
                app = create_app({
                    "TESTING": True,
                    "SECRET_KEY": "test-secret",
                    "USER_DATABASE": database_path,
                })
            category = milestone.create_category(
                database_path, "Kết cấu", None, "2026-10-01"
            )
            task_ids = {
                task["ten"]: task["id"] for task in cong_viec.list_tasks(database_path)
            }
            first = task_ids["Chuẩn bị mặt bằng"]
            second = task_ids["Kiểm tra vật tư"]
            milestone.assign_task(database_path, category["id"], first)
            milestone.assign_task(database_path, category["id"], second)
            client = app.test_client()
            csrf = client.get("/api/auth/csrf").get_json()["csrf_token"]
            login = client.post(
                "/api/auth/login",
                json={"username": "admin", "password": "test-admin-password"},
                headers={"X-CSRF-Token": csrf},
            )
            csrf = login.get_json()["csrf_token"]

            response = client.post(
                f"/api/categories/{category['id']}/dependencies",
                json={
                    "task_id": second,
                    "depends_on_task_id": first,
                    "relationship_type": "FF",
                },
                headers={"X-CSRF-Token": csrf},
            )

            self.assertEqual(response.status_code, 201)
            self.assertEqual(
                milestone.list_dependencies(database_path, category["id"]),
                [{
                    "task_id": second,
                    "depends_on_task_id": first,
                    "relationship_type": "FF",
                }],
            )

    def test_cyclic_dependency_returns_422_with_task_names(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = str(Path(temp_dir) / "users.db")
            with patch.dict(os.environ, {
                "INITIAL_ADMIN_USERNAME": "admin",
                "INITIAL_ADMIN_PASSWORD": "test-admin-password",
            }):
                app = create_app({
                    "TESTING": True,
                    "SECRET_KEY": "test-secret",
                    "USER_DATABASE": database_path,
                })
            category = milestone.create_category(
                database_path, "Kết cấu", None, "2026-10-01"
            )
            tasks_by_name = {
                task["ten"]: task["id"] for task in cong_viec.list_tasks(database_path)
            }
            first_name = "Chuẩn bị mặt bằng"
            second_name = "Kiểm tra vật tư"
            first, second = tasks_by_name[first_name], tasks_by_name[second_name]
            milestone.assign_task(database_path, category["id"], first)
            milestone.assign_task(database_path, category["id"], second)
            milestone.add_dependency(database_path, second, first)

            client = app.test_client()
            csrf = client.get("/api/auth/csrf").get_json()["csrf_token"]
            login_response = client.post(
                "/api/auth/login",
                json={"username": "admin", "password": "test-admin-password"},
                headers={"X-CSRF-Token": csrf},
            )
            csrf = login_response.get_json()["csrf_token"]
            response = client.post(
                f"/api/categories/{category['id']}/dependencies",
                json={"task_id": first, "depends_on_task_id": second},
                headers={"X-CSRF-Token": csrf},
            )

            self.assertEqual(response.status_code, 422)
            self.assertEqual(response.get_json()["error"], "dependency_cycle")
            self.assertIn(f"{first_name} chờ {second_name}", response.get_json()["message"])
            self.assertIn(f"{second_name} lại chờ {first_name}", response.get_json()["message"])
            self.assertEqual(
                milestone.list_dependencies(database_path, category["id"]),
                [{
                    "task_id": second,
                    "depends_on_task_id": first,
                    "relationship_type": "FS",
                }],
            )

    def test_progress_update_saves_category_id(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = str(Path(temp_dir) / "users.db")
            with patch.dict(os.environ, {
                "INITIAL_ADMIN_USERNAME": "admin",
                "INITIAL_ADMIN_PASSWORD": "test-admin-password",
            }):
                app = create_app({
                    "TESTING": True,
                    "SECRET_KEY": "test-secret",
                    "USER_DATABASE": database_path,
                })
            category = milestone.create_category(
                database_path, "Kết cấu", None, "2026-10-01"
            )
            client = app.test_client()

            csrf = client.get("/api/auth/csrf").get_json()["csrf_token"]
            login_response = client.post(
                "/api/auth/login",
                json={"username": "admin", "password": "test-admin-password"},
                headers={"X-CSRF-Token": csrf},
            )
            csrf = login_response.get_json()["csrf_token"]
            task_id = cong_viec.list_tasks(database_path)[0]["id"]
            response = client.patch(
                f"/api/cong-viec/{task_id}",
                json={
                    "ngay_bat_dau_thuc_te": None,
                    "ngay_ket_thuc_thuc_te": None,
                    "phan_tram_hoan_thanh": 0,
                    "category_id": category["id"],
                },
                headers={"X-CSRF-Token": csrf},
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json()["category_id"], category["id"])
            stored_task = next(
                task for task in cong_viec.list_tasks(database_path)
                if task["id"] == task_id
            )
            self.assertEqual(stored_task["category_id"], category["id"])
            self.assertEqual(
                milestone.list_categories(database_path)[0]["tasks"][0]["id"],
                task_id,
            )

    def test_viewer_cannot_create_milestone(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = str(Path(temp_dir) / "users.db")
            with patch.dict(os.environ, {
                "INITIAL_ADMIN_USERNAME": "admin",
                "INITIAL_ADMIN_PASSWORD": "test-admin-password",
            }):
                app = create_app({
                    "TESTING": True,
                    "SECRET_KEY": "test-secret",
                    "USER_DATABASE": database_path,
                })
            user.create_user(database_path, "viewer", "Viewer", "test-viewer-password", "viewer")
            client = app.test_client()

            csrf = client.get("/api/auth/csrf").get_json()["csrf_token"]
            login_response = client.post(
                "/api/auth/login",
                json={"username": "viewer", "password": "test-viewer-password"},
                headers={"X-CSRF-Token": csrf},
            )
            self.assertEqual(login_response.status_code, 200)
            csrf = login_response.get_json()["csrf_token"]

            response = client.post(
                "/api/milestones",
                json={"category_id": 1, "deadline": "2026-10-02"},
                headers={"X-CSRF-Token": csrf},
            )

            self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
