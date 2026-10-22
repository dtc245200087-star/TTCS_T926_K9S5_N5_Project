"""S-34: 20 offline diaries + image retries after network recovery.

An integration-level network simulation: requests are held in a durable-looking local
queue until connectivity is restored. This verifies the real Flask endpoints and
SQLite idempotency, not browser IndexedDB/Service Worker behavior.
"""
import io
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from app import create_app
from app.models import cong_viec, nhat_ky, user as users


class OfflineTwentyDiarySyncTests(unittest.TestCase):
    PROJECT = "Khu đô thị Bắc Sông Cầu"
    DIARY_DATE = "2026-10-19"

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.database_path = str(Path(self.temporary.name) / "users.db")
        with patch.dict(os.environ, {
            "INITIAL_ADMIN_USERNAME": "admin",
            "INITIAL_ADMIN_PASSWORD": "test-admin-password",
        }):
            app = create_app({
                "TESTING": True,
                "SECRET_KEY": "s34-test-secret",
                "USER_DATABASE": self.database_path,
                "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            })
        
        self.client = app.test_client()

        users.initialize_database(self.database_path)
        users.create_user(
            self.database_path,
            username="admin",
            full_name="Test Admin",
            password="test-admin-password",
            role="admin",
        )
        nhat_ky.initialize_database(self.database_path)

        csrf = self.client.get("/api/auth/csrf").get_json()["csrf_token"]
        login = self.client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "test-admin-password"},
            headers={"X-CSRF-Token": csrf},
        )
        self.assertEqual(login.status_code, 200)
        self.headers = {"X-CSRF-Token": login.get_json()["csrf_token"]}
        self.task_id = next(task["id"] for task in cong_viec.list_tasks(self.database_path)
                            if task["cong_trinh"] == self.PROJECT)

    def tearDown(self):
    	import gc
    	import sqlite3
    	import time

    	gc.collect()

    	for attempt in range(5):
            try:
            	self.temporary.cleanup()
            	break
            except PermissionError:
            	if attempt == 4:
                    raise
            	time.sleep(0.2)
            	gc.collect()

    def test_twenty_offline_entries_with_images_sync_once_under_three_minutes(self):
        started = time.monotonic()
        # Simulate loss of connectivity: create local payloads but send no HTTP requests.
        online = False
        queue = [
            {
                "client_uid": f"s34-offline-diary-{i:02d}",
                "cong_trinh": self.PROJECT,
                "ngay": self.DIARY_DATE,
                "cong_viec_id": self.task_id,
                "gio": f"{8 + i // 60:02d}:{i % 60:02d}",
                "noi_dung": f"Nhat ky ngoai tuyen {i:02d}",
                "upload_id": f"s34-offline-photo-{i:02d}",
            }
            for i in range(20)
        ]
        self.assertFalse(online)
        self.assertEqual(len(queue), 20)
        before = self.client.get("/api/nhat-ky", query_string={
            "cong_trinh": self.PROJECT, "ngay": self.DIARY_DATE,
        }).get_json()
        self.assertEqual(before, [])

        # Reconnect. Re-send every request (as if an HTTP reply were lost).
        online = True
        completed = []
        if online:
            for item in queue:
                payload = {key: item[key] for key in (
                    "client_uid", "cong_trinh", "ngay", "cong_viec_id", "gio", "noi_dung"
                )}
                first = self.client.post("/api/nhat-ky", json=payload, headers=self.headers)
                self.assertIn(first.status_code, (200, 201), first.get_json())
                retry = self.client.post("/api/nhat-ky", json=payload, headers=self.headers)
                self.assertEqual(retry.status_code, 200, retry.get_json())
                self.assertEqual(retry.get_json()["id"], first.get_json()["id"])
                entry_id = first.get_json()["id"]

                def upload():
                    return self.client.post(
                        f"/api/nhat-ky/{entry_id}/images",
                        data={
                            "upload_id": item["upload_id"],
                            "ghi_chu_anh": f"Anh {item['client_uid']}",
                            "image": (io.BytesIO(b"\xff\xd8\xff" + b"image-data"), "photo.jpg"),
                            "thumbnail": (io.BytesIO(b"\xff\xd8\xff" + b"thumb-data"), "thumb.jpg"),
                        },
                        headers=self.headers,
                    )

                first_image = upload()
                self.assertEqual(first_image.status_code, 201, first_image.get_json())
                retry_image = upload()
                self.assertEqual(retry_image.status_code, 200, retry_image.get_json())
                self.assertEqual(first_image.get_json(), retry_image.get_json())
                completed.append(item["client_uid"])
                self.assertLess(time.monotonic() - started, 180, "S-34 exceeded 3-minute limit")

        self.assertEqual(len(completed), 20)
        after = self.client.get("/api/nhat-ky", query_string={
            "cong_trinh": self.PROJECT, "ngay": self.DIARY_DATE,
        })
        self.assertEqual(after.status_code, 200)
        entries = after.get_json()
        self.assertEqual(len(entries), 20, "missing or duplicate diary entries")
        self.assertEqual({entry["client_uid"] for entry in entries}, set(completed))
        self.assertEqual(len({entry["id"] for entry in entries}), 20)
        for entry in entries:
            self.assertEqual(len(entry["images"]), 1, "missing or duplicate image")
            img = entry["images"][0]
            response = self.client.get(img["url"], buffered=True)
            self.assertEqual(response.status_code, 200)
            response.close()

            response = self.client.get(img["thumbnail_url"], buffered=True)
            self.assertEqual(response.status_code, 200)
            response.close()
        self.assertLess(time.monotonic() - started, 180)


if __name__ == "__main__":
    unittest.main()
