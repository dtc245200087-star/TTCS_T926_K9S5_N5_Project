import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from app import migrations
from app.models import project_work_items


class ProjectWorkItemMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = str(Path(self.temp_dir.name) / "test.db")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_upgrade_creates_tables_constraints_and_parent_index(self):
        migrations.upgrade_database(self.database_path)
        migrations.upgrade_database(self.database_path)

        with closing(sqlite3.connect(self.database_path)) as db:
            tables = {
                row[0]
                for row in db.execute(
                    """SELECT name FROM sqlite_master
                       WHERE type = 'table'"""
                )
            }
            indexes = {
                row[1] for row in db.execute("PRAGMA index_list(work_items)")
            }
            versions = db.execute(
                "SELECT version FROM schema_migrations ORDER BY version"
            ).fetchall()

        self.assertIn("projects", tables)
        self.assertIn("work_items", tables)
        self.assertIn("idx_work_items_parent_id", indexes)
        self.assertEqual(versions, [(1,)])

    def test_downgrade_removes_only_the_new_schema(self):
        with closing(sqlite3.connect(self.database_path)) as db:
            db.execute("CREATE TABLE legacy_data (id INTEGER PRIMARY KEY)")
            db.commit()

        migrations.upgrade_database(self.database_path)
        migrations.downgrade_database(self.database_path)

        with closing(sqlite3.connect(self.database_path)) as db:
            tables = {
                row[0]
                for row in db.execute(
                    """SELECT name FROM sqlite_master
                       WHERE type = 'table'"""
                )
            }
            versions = db.execute(
                "SELECT version FROM schema_migrations ORDER BY version"
            ).fetchall()

        self.assertIn("legacy_data", tables)
        self.assertNotIn("projects", tables)
        self.assertNotIn("work_items", tables)
        self.assertEqual(versions, [])

        migrations.upgrade_database(self.database_path)
        with closing(sqlite3.connect(self.database_path)) as db:
            tables = {
                row[0]
                for row in db.execute(
                    """SELECT name FROM sqlite_master
                       WHERE type = 'table'"""
                )
            }
        self.assertIn("legacy_data", tables)
        self.assertIn("projects", tables)
        self.assertIn("work_items", tables)


class ProjectWorkItemTreeTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = str(Path(self.temp_dir.name) / "test.db")
        migrations.upgrade_database(self.database_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_tree_query_returns_all_descendants_in_nested_shape(self):
        project = project_work_items.create_project(self.database_path, "Project A")
        other_project = project_work_items.create_project(
            self.database_path, "Project B"
        )
        root = project_work_items.create_work_item(
            self.database_path, project["id"], "Foundation"
        )
        child = project_work_items.create_work_item(
            self.database_path, project["id"], "Pour concrete", root["id"]
        )
        grandchild = project_work_items.create_work_item(
            self.database_path, project["id"], "Cure concrete", child["id"]
        )
        sibling = project_work_items.create_work_item(
            self.database_path, project["id"], "Install rebar", root["id"]
        )
        project_work_items.create_work_item(
            self.database_path, other_project["id"], "Unrelated item"
        )

        tree = project_work_items.get_work_item_tree(
            self.database_path, root["id"]
        )

        self.assertEqual(tree["id"], root["id"])
        self.assertEqual(
            [item["id"] for item in tree["children"]],
            [child["id"], sibling["id"]],
        )
        self.assertEqual(tree["children"][0]["children"][0]["id"], grandchild["id"])
        self.assertEqual(tree["children"][1]["children"], [])
        self.assertIsNone(
            project_work_items.get_work_item_tree(self.database_path, -1)
        )

    def test_foreign_keys_reject_missing_project_and_cross_project_parent(self):
        project = project_work_items.create_project(self.database_path, "Project A")
        other_project = project_work_items.create_project(
            self.database_path, "Project B"
        )
        parent = project_work_items.create_work_item(
            self.database_path, project["id"], "Parent"
        )

        with self.assertRaises(sqlite3.IntegrityError):
            project_work_items.create_work_item(
                self.database_path, -1, "Missing project"
            )
        with self.assertRaises(sqlite3.IntegrityError):
            project_work_items.create_work_item(
                self.database_path, other_project["id"], "Wrong project parent",
                parent["id"],
            )

    def test_database_rejects_parent_cycle(self):
        project = project_work_items.create_project(self.database_path, "Project A")
        root = project_work_items.create_work_item(
            self.database_path, project["id"], "Root"
        )
        child = project_work_items.create_work_item(
            self.database_path, project["id"], "Child", root["id"]
        )

        with closing(sqlite3.connect(self.database_path)) as db:
            db.execute("PRAGMA foreign_keys = ON")
            with self.assertRaisesRegex(
                sqlite3.IntegrityError, "work_item_parent_cycle"
            ):
                db.execute(
                    "UPDATE work_items SET parent_id = ? WHERE id = ?",
                    (child["id"], root["id"]),
                )
            db.rollback()


if __name__ == "__main__":
    unittest.main()
