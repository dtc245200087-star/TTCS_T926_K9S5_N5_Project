
import unittest
import tempfile
from pathlib import Path

from app import create_app
from app.models import user as users, cong_viec


class AcceptanceTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(
            ignore_cleanup_errors=True
        )
        self.db_path = str(Path(self.temp.name) / "users.db")

        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "USER_DATABASE": self.db_path,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        })

        users.initialize_database(self.db_path)
        users.create_user(
            self.db_path,
            "admin",
            "Test Admin",
            "test-admin-password",
            "admin",
        )

        self.client = self.app.test_client()
        csrf = self.client.get("/api/auth/csrf").get_json()["csrf_token"]

        login = self.client.post(
            "/api/auth/login",
            json={
                "username": "admin",
                "password": "test-admin-password",
            },
            headers={"X-CSRF-Token": csrf},
        )

        self.assertEqual(login.status_code, 200)
        self.headers = {
            "X-CSRF-Token": login.get_json()["csrf_token"]
        }

        tasks = self.client.get("/api/acceptance/tasks")
        self.assertEqual(tasks.status_code, 200)

        self.task = next(
            task for task in tasks.get_json()
            if task.get("cong_trinh")
        )
        self.project = self.task["cong_trinh"]

    def tearDown(self):
        self.temp.cleanup()

    def create_batch(self, cumulative):
        return self.client.post(
            "/api/acceptance",
            json={
                "project": self.project,
                "batch_date": "2026-10-20",
                "lines": [{
                    "task_id": self.task["id"],
                    "cumulative": cumulative,
                }],
            },
            headers=self.headers,
        )

    def test_create_first_batch(self):
        response = self.create_batch(30)

        self.assertEqual(
            response.status_code, 201,
            response.get_json()
        )

        data = response.get_json()
        self.assertEqual(data["status"], "draft")

    def test_approved_cumulative_quantity(self):
        first = self.create_batch(30)
        self.assertEqual(first.status_code, 201, first.get_json())

        first_id = first.get_json()["id"]

        approved = self.client.post(
            f"/api/acceptance/{first_id}/approve",
            headers=self.headers,
        )
        self.assertEqual(approved.status_code, 200, approved.get_json())

        second = self.create_batch(65)
        self.assertEqual(second.status_code, 201, second.get_json())

        data = second.get_json()
        line = data["lines"][0]

        self.assertAlmostEqual(float(line["quantity"]), 35)

    def test_reject_smaller_cumulative(self):
        first = self.create_batch(50)
        self.assertEqual(first.status_code, 201, first.get_json())

        first_id = first.get_json()["id"]
        approved = self.client.post(
            f"/api/acceptance/{first_id}/approve",
            headers=self.headers,
        )
        self.assertEqual(approved.status_code, 200, approved.get_json())

        second = self.create_batch(20)
        self.assertEqual(second.status_code, 400)


if __name__ == "__main__":
    unittest.main()