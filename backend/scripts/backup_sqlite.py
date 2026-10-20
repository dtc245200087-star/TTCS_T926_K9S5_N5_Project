"""Create verified, timestamped backups of the application's SQLite databases."""

import json
import logging
import re
import shutil
import sqlite3
import sys
import tempfile
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path


# These fixed paths keep the source inside the read-only database mount.
DATABASE_DIR = Path("/app/instance")
BACKUP_DIR = Path("/backups")
DATABASE_NAMES = ("app.db", "users.db")
BACKUP_NAME_PATTERN = re.compile(r"^backup_\d{8}T\d{6}Z$")
KEEP_BACKUPS = 7

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


def table_row_counts(database_path):
    """Return row counts for every user-created table in a SQLite database."""
    with closing(sqlite3.connect(database_path)) as database:
        table_names = [
            row[0]
            for row in database.execute(
                """SELECT name FROM sqlite_master
                   WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                   ORDER BY name"""
            )
        ]
        counts = {}
        for table_name in table_names:
            quoted_name = '"' + table_name.replace('"', '""') + '"'
            counts[table_name] = database.execute(
                f"SELECT COUNT(*) FROM {quoted_name}"
            ).fetchone()[0]
        return counts


def verify_database(database_path):
    """Reject a backup file unless SQLite reports it as structurally sound."""
    with closing(sqlite3.connect(database_path)) as database:
        result = database.execute("PRAGMA integrity_check").fetchone()[0]
    if result != "ok":
        raise sqlite3.DatabaseError(
            f"SQLite integrity check failed for {database_path}: {result}"
        )


def prune_old_backups():
    """Keep only the seven newest completed backup bundles."""
    completed_backups = sorted(
        (
            path
            for path in BACKUP_DIR.iterdir()
            if path.is_dir()
            and BACKUP_NAME_PATTERN.fullmatch(path.name)
            and (path / "_COMPLETE.json").is_file()
        ),
        key=lambda path: path.name,
        reverse=True,
    )

    for old_backup in completed_backups[KEEP_BACKUPS:]:
        # Restrict cleanup to completed timestamped bundles directly under BACKUP_DIR.
        if old_backup.resolve().parent != BACKUP_DIR.resolve():
            raise OSError(f"Refusing to remove unexpected backup path: {old_backup}")
        logger.info("Removing old backup bundle: %s", old_backup.name)
        shutil.rmtree(old_backup)


def create_backup():
    """Build a complete bundle in a temporary directory, then publish it."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_name = f"backup_{timestamp}"
    final_directory = BACKUP_DIR / backup_name

    if final_directory.exists():
        raise FileExistsError(f"Backup already exists; refusing to overwrite: {backup_name}")

    staging_directory = Path(
        tempfile.mkdtemp(prefix=f".{backup_name}.", dir=BACKUP_DIR)
    )
    published = False
    try:
        manifest = {"created_at": timestamp, "databases": {}}
        for database_name in DATABASE_NAMES:
            source_path = DATABASE_DIR / database_name
            if not source_path.is_file():
                raise FileNotFoundError(
                    f"Required application database was not found: {source_path}"
                )

            backup_path = staging_directory / database_name
            # Open the live database read-only and use SQLite's online backup API;
            # this safely includes committed data even while the application is running.
            source_uri = source_path.resolve().as_uri() + "?mode=ro"
            with closing(
                sqlite3.connect(source_uri, uri=True, timeout=30)
            ) as source_db, closing(
                sqlite3.connect(backup_path, timeout=30)
            ) as destination_db:
                source_db.backup(destination_db)
                destination_db.commit()

            verify_database(backup_path)
            manifest["databases"][database_name] = table_row_counts(backup_path)
            logger.info("Backed up and verified %s", database_name)

        # This marker distinguishes complete bundles from interrupted staging data.
        (staging_directory / "_COMPLETE.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        staging_directory.rename(final_directory)
        published = True
        logger.info("Published backup bundle: %s", final_directory)
        prune_old_backups()
    finally:
        # Only remove the temporary directory created by this invocation.
        if not published and staging_directory.exists():
            shutil.rmtree(staging_directory)


def main():
    try:
        create_backup()
    except (OSError, sqlite3.Error):
        logger.exception("SQLite backup failed")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
