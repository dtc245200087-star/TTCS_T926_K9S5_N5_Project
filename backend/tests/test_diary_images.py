import io
import os
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlencode
from unittest.mock import patch

from app import create_app
from app.models import cong_viec


class DiaryImageUploadTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = str(Path(self.temp_dir.name) / "users.db")
        with patch.dict(os.environ, {
            "INITIAL_ADMIN_USERNAME": "admin",
            "INITIAL_ADMIN_PASSWORD": "test-admin-password",
        }):
            app = create_app({
                "TESTING": True,
                "SECRET_KEY": "test-secret",
                "USER_DATABASE": self.database_path,
            })
        self.client = app.test_client()
        csrf = self.client.get("/api/auth/csrf").get_json()["csrf_token"]
        login = self.client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "test-admin-password"},
            headers={"X-CSRF-Token": csrf},
        )
        self.csrf = login.get_json()["csrf_token"]
        self.task_id = next(
            task["id"] for task in cong_viec.list_tasks(self.database_path)
            if task["cong_trinh"] == "Khu đô thị Bắc Sông Cầu"
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_entry(self):
        response = self.client.post(
            "/api/nhat-ky",
            json={
                "cong_trinh": "Khu đô thị Bắc Sông Cầu",
                "ngay": "2026-10-15",
                "cong_viec_id": self.task_id,
                "gio": "08:30",
                "noi_dung": "Thi công tại hiện trường.",
            },
            headers={"X-CSRF-Token": self.csrf},
        )
        self.assertEqual(response.status_code, 201)
        return response.get_json()

    def upload_image(self, entry_id, upload_id, content=b"\xff\xd8\xffimage-data"):
        return self.client.post(
            f"/api/nhat-ky/{entry_id}/images",
            data={
                "ghi_chu_anh": "Ảnh thi công móng khối A",
                "upload_id": upload_id,
                "image": (io.BytesIO(content), "site.jpg"),
                "thumbnail": (io.BytesIO(b"\xff\xd8\xffthumbnail"), "site-thumb.jpg"),
            },
            headers={"X-CSRF-Token": self.csrf},
        )

    def test_entry_is_saved_before_separate_image_upload_and_retry_is_idempotent(self):
        entry = self.create_entry()
        response = self.upload_image(entry["id"], "client-image-1")
        self.assertEqual(response.status_code, 201)
        image = response.get_json()
        self.assertEqual(image["ghi_chu"], "Ảnh thi công móng khối A")
        saved_image = self.client.get(image["url"])
        self.assertEqual(saved_image.status_code, 200)
        self.assertTrue(saved_image.data.startswith(b"\xff\xd8\xff"))
        saved_thumbnail = self.client.get(image["thumbnail_url"])
        self.assertEqual(saved_thumbnail.status_code, 200)
        self.assertTrue(saved_thumbnail.data.startswith(b"\xff\xd8\xff"))
        retry = self.upload_image(entry["id"], "client-image-1")
        self.assertEqual(retry.status_code, 200)
        self.assertEqual(retry.get_json(), image)
        query = urlencode({
            "cong_trinh": "Khu đô thị Bắc Sông Cầu",
            "ngay": "2026-10-15",
        })
        listed = self.client.get(f"/api/nhat-ky?{query}")
        self.assertEqual(listed.status_code, 200)
        saved_entries = [item for item in listed.get_json() if item["id"] == entry["id"]]
        self.assertEqual(saved_entries[0]["images"], [image])

    def test_rejects_file_without_matching_image_signature(self):
        entry = self.create_entry()
        response = self.upload_image(entry["id"], "client-image-bad", b"not-an-image")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "invalid_image")

    def test_entry_remains_saved_if_image_upload_fails(self):
        entry = self.create_entry()
        response = self.client.post(
            f"/api/nhat-ky/{entry['id']}/images",
            data={"upload_id": "failed-image"},
            headers={"X-CSRF-Token": self.csrf},
        )
        self.assertEqual(response.status_code, 400)
        query = urlencode({
            "cong_trinh": "Khu đô thị Bắc Sông Cầu",
            "ngay": "2026-10-15",
        })
        listed = self.client.get(f"/api/nhat-ky?{query}")
        self.assertIn(entry["id"], [item["id"] for item in listed.get_json()])
