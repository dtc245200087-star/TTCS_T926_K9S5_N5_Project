"""Versioned SQLite migrations for application-owned schema changes."""

import sqlite3
from contextlib import closing


_MIGRATIONS = (
    (
        1,
        "create_projects_and_work_items",
        (
            """CREATE TABLE projects (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL,
                   created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
               )""",
            """CREATE TABLE work_items (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   project_id INTEGER NOT NULL
                       REFERENCES projects(id) ON DELETE CASCADE,
                   parent_id INTEGER,
                   name TEXT NOT NULL,
                   created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                   UNIQUE (project_id, id),
                   FOREIGN KEY (project_id, parent_id)
                       REFERENCES work_items(project_id, id) ON DELETE CASCADE,
                   CHECK (parent_id IS NULL OR parent_id != id)
               )""",
            "CREATE INDEX idx_work_items_parent_id ON work_items(parent_id)",
            """CREATE TRIGGER work_items_prevent_parent_cycle
               BEFORE UPDATE OF parent_id ON work_items
               WHEN NEW.parent_id IS NOT NULL
               BEGIN
                   SELECT CASE WHEN EXISTS (
                       WITH RECURSIVE descendants(id) AS (
                           SELECT id FROM work_items WHERE id = OLD.id
                           UNION ALL
                           SELECT child.id
                           FROM work_items child
                           JOIN descendants parent ON child.parent_id = parent.id
                       )
                       SELECT 1 FROM descendants WHERE id = NEW.parent_id
                   )
                   THEN RAISE(ABORT, 'work_item_parent_cycle') END;
               END""",
        ),
        (
            "DROP TRIGGER work_items_prevent_parent_cycle",
            "DROP INDEX idx_work_items_parent_id",
            "DROP TABLE work_items",
            "DROP TABLE projects",
        ),
    ),
)


def _connect(database_path):
    db = sqlite3.connect(database_path, timeout=10)
    db.execute("PRAGMA foreign_keys = ON")
    return db


def _ensure_migration_table(db):
    db.execute(
        """CREATE TABLE IF NOT EXISTS schema_migrations (
               version INTEGER PRIMARY KEY,
               name TEXT NOT NULL,
               applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
           )"""
    )


def upgrade_database(database_path):
    """Apply all pending migrations to the database."""
    with closing(_connect(database_path)) as db:
        _ensure_migration_table(db)
        db.commit()
        applied = {
            row[0]
            for row in db.execute("SELECT version FROM schema_migrations").fetchall()
        }
        unknown_versions = applied - {migration[0] for migration in _MIGRATIONS}
        if unknown_versions:
            raise RuntimeError(
                "Cannot upgrade unknown migration version(s): "
                + ", ".join(str(version) for version in sorted(unknown_versions))
            )
        for version, name, statements, _ in _MIGRATIONS:
            if version in applied:
                continue
            try:
                db.execute("BEGIN IMMEDIATE")
                if db.execute(
                    "SELECT 1 FROM schema_migrations WHERE version = ?", (version,)
                ).fetchone():
                    db.commit()
                    continue
                for statement in statements:
                    db.execute(statement)
                db.execute(
                    "INSERT INTO schema_migrations (version, name) VALUES (?, ?)",
                    (version, name),
                )
                db.commit()
            except sqlite3.Error:
                db.rollback()
                raise


def downgrade_database(database_path, target_version=0):
    """Roll applied migrations back to target_version."""
    if not isinstance(target_version, int) or target_version < 0:
        raise ValueError("target_version must be a non-negative integer")

    with closing(_connect(database_path)) as db:
        _ensure_migration_table(db)
        db.commit()
        applied = {
            row[0]
            for row in db.execute("SELECT version FROM schema_migrations").fetchall()
        }
        available_versions = {migration[0] for migration in _MIGRATIONS}
        unknown_versions = applied - available_versions
        if unknown_versions:
            raise RuntimeError(
                "Cannot downgrade unknown migration version(s): "
                + ", ".join(str(version) for version in sorted(unknown_versions))
            )

        for version, _, _, statements in reversed(_MIGRATIONS):
            if version <= target_version or version not in applied:
                continue
            try:
                db.execute("BEGIN IMMEDIATE")
                if not db.execute(
                    "SELECT 1 FROM schema_migrations WHERE version = ?", (version,)
                ).fetchone():
                    db.commit()
                    continue
                for statement in statements:
                    db.execute(statement)
                db.execute(
                    "DELETE FROM schema_migrations WHERE version = ?", (version,)
                )
                db.commit()
            except sqlite3.Error:
                db.rollback()
                raise
