
import unittest
from concurrent.futures import ThreadPoolExecutor
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

        self.client = self.app.test_client()
        csrf = self.client.get("/api/auth/csrf").get_json()["csrf_token"]

        login = self.client.post(
            "/api/auth/login",
            json={
                "username": "admin",
                "password": "admin12345678",
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
        self.set_contract(1000)

    def set_contract(self, amount):
        response = self.client.put(
            f'/api/acceptance/contracts/{self.task["id"]}',
            json={'contract_quantity': amount}, headers=self.headers,
        )
        self.assertEqual(response.status_code, 200, response.get_json())

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

    def test_approval_rejects_contract_overflow(self):
        self.set_contract(40)
        response = self.create_batch(41)
        self.assertEqual(response.status_code, 201, response.get_json())
        result = self.client.post(
            f'/api/acceptance/{response.get_json()["id"]}/approve', headers=self.headers,
        )
        self.assertEqual(result.status_code, 409, result.get_json())

    def test_contract_cannot_be_reduced_below_approved(self):
        first = self.create_batch(30)
        self.assertEqual(first.status_code, 201)
        approved = self.client.post(
            f'/api/acceptance/{first.get_json()["id"]}/approve', headers=self.headers,
        )
        self.assertEqual(approved.status_code, 200)
        response = self.client.put(
            f'/api/acceptance/contracts/{self.task["id"]}',
            json={'contract_quantity': 29}, headers=self.headers,
        )
        self.assertEqual(response.status_code, 409)

    def test_concurrent_over_limit_approvals_are_rejected(self):
        self.set_contract(50)
        batches = [self.create_batch(60), self.create_batch(70)]
        ids = [b.get_json()['id'] for b in batches]
        self.assertTrue(all(b.status_code == 201 for b in batches))

        def approve(batch_id):
            with self.app.test_client() as client:
                with client.session_transaction() as session:
                    session['user_id'] = 1
                    session['csrf_token'] = 'concurrent-test'
                return client.post(f'/api/acceptance/{batch_id}/approve',
                                   headers={'X-CSRF-Token':'concurrent-test'}).status_code

        with ThreadPoolExecutor(max_workers=2) as executor:
            statuses = list(executor.map(approve, ids))
        self.assertEqual(statuses, [409, 409])

    def test_concurrent_approvals_cannot_exceed_contract(self):
        self.set_contract(50)
        batches = [self.create_batch(40), self.create_batch(40)]
        for batch in batches:
            self.assertEqual(batch.status_code, 201, batch.get_json())
        ids = [batch.get_json()['id'] for batch in batches]

        def approve(batch_id):
            # Each request gets its own client/session and SQLite connection.
            with self.app.test_client() as client:
                with client.session_transaction() as session:
                    session['user_id'] = 1
                    session['csrf_token'] = 'concurrent-test'
                response = client.post(f'/api/acceptance/{batch_id}/approve',
                                       headers={'X-CSRF-Token':'concurrent-test'})
                return response.status_code

        with ThreadPoolExecutor(max_workers=2) as executor:
            statuses = list(executor.map(approve, ids))
        self.assertEqual(sorted(statuses), [200, 409], statuses)
        listed = self.client.get('/api/acceptance').get_json()
        approved = [batch for batch in listed if batch['id'] in ids and batch['status']=='approved']
        self.assertEqual(len(approved), 1)


if __name__ == "__main__":
    unittest.main()