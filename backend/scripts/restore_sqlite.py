"""Restore one backup database into a dedicated, empty test database.

PowerShell examples from the repository root:
    docker compose run --rm restore backup_20261018T133831Z app.db
    docker compose run --rm restore --backup backup_20261018T133831Z --database app.db
"""

import argparse
import logging
import re
import sqlite3
import sys
from contextlib import closing
from pathlib import Path


# This service intentionally has no mount for the application's live database volume.
BACKUP_DIR = Path("/backups")
RESTORE_DIR = Path("/restore-test")
RESTORE_DATABASE = RESTORE_DIR / "test_restore.db"
BACKUP_NAME_PATTERN = re.compile(r"^backup_\d{8}T\d{6}Z$")
ALLOWED_DATABASES = ("app.db", "users.db")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


def table_row_counts(database_path):
    """Count records in every user-created table, in stable table-name order."""
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
    """Check SQLite integrity and ensure all foreign keys point to valid rows."""
    with closing(sqlite3.connect(database_path)) as database:
        integrity = database.execute("PRAGMA integrity_check").fetchone()[0]
        foreign_key_errors = database.execute("PRAGMA foreign_key_check").fetchall()
    if integrity != "ok":
        raise sqlite3.DatabaseError(
            f"SQLite integrity check failed for {database_path}: {integrity}"
        )
    if foreign_key_errors:
        raise sqlite3.DatabaseError(
            f"Foreign key check failed for {database_path}: "
            f"{len(foreign_key_errors)} violation(s)"
        )


def parse_arguments():
    """Accept either positional arguments or their named flag equivalents."""
    parser = argparse.ArgumentParser(
        description="Restore a backup into /restore-test/test_restore.db only."
    )
    parser.add_argument(
        "--backup",
        dest="backup_option",
        help="Timestamped bundle name, for example backup_20261018T130000Z",
    )
    parser.add_argument(
        "--database",
        choices=ALLOWED_DATABASES,
        help="Database file inside the selected bundle",
    )
    parser.add_argument(
        "backup_positional",
        nargs="?",
        help="Timestamped bundle name (positional alternative to --backup)",
    )
    parser.add_argument(
        "database_positional",
        nargs="?",
        choices=ALLOWED_DATABASES,
        help="Database file (positional alternative to --database)",
    )
    return parser, parser.parse_args()


def restore(backup_name, database_name):
    """Restore into a newly created test file; never access the live DB volume."""
    if not BACKUP_NAME_PATTERN.fullmatch(backup_name):
        raise ValueError("Backup name must be a timestamped backup bundle name.")

    backup_root = BACKUP_DIR.resolve(strict=True)
    bundle = BACKUP_DIR / backup_name
    if bundle.is_symlink() or bundle.resolve(strict=True).parent != backup_root:
        raise ValueError("Backup bundle must be a direct child of /backups.")
    if not bundle.is_dir() or not (bundle / "_COMPLETE.json").is_file():
        raise FileNotFoundError(f"Complete backup bundle was not found: {backup_name}")

    source_path = bundle / database_name
    if source_path.is_symlink() or not source_path.is_file():
        raise FileNotFoundError(f"Backup database was not found: {source_path}")

    RESTORE_DIR.mkdir(parents=True, exist_ok=True)
    if RESTORE_DIR.is_symlink():
        raise ValueError("Restore directory must be the dedicated /restore-test mount.")
    if RESTORE_DATABASE.exists() or RESTORE_DATABASE.is_symlink():
        raise FileExistsError(
            f"Refusing to overwrite an existing restore target: {RESTORE_DATABASE}"
        )

    counts_before = table_row_counts(source_path)
    target_created = False
    try:
        # Exclusive creation guarantees a pre-existing database cannot be overwritten.
        with RESTORE_DATABASE.open("xb"):
            target_created = True

        source_uri = source_path.resolve().as_uri() + "?mode=ro"
        with closing(
            sqlite3.connect(source_uri, uri=True, timeout=30)
        ) as source_db, closing(
            sqlite3.connect(RESTORE_DATABASE, timeout=30)
        ) as destination_db:
            source_db.backup(destination_db)
            destination_db.commit()

        verify_database(RESTORE_DATABASE)
        counts_after = table_row_counts(RESTORE_DATABASE)
        logger.info("Record counts in backup before restore: %s", counts_before)
        logger.info("Record counts in test database after restore: %s", counts_after)
        if counts_before != counts_after:
            raise sqlite3.DatabaseError(
                "Restore verification failed: table record counts differ."
            )
        logger.info("Restore verified successfully at %s", RESTORE_DATABASE)
    except (OSError, sqlite3.Error, ValueError):
        # Remove only the target file created by this restore attempt if it failed.
        if target_created and RESTORE_DATABASE.exists():
            RESTORE_DATABASE.unlink()
        raise


def main():
    parser, arguments = parse_arguments()
    if (
        arguments.backup_option
        and arguments.backup_positional
        and arguments.backup_option != arguments.backup_positional
    ):
        parser.error("positional bundle name and --backup must match")
    if (
        arguments.database
        and arguments.database_positional
        and arguments.database != arguments.database_positional
    ):
        parser.error("positional database name and --database must match")

    backup_name = arguments.backup_option or arguments.backup_positional
    database_name = arguments.database or arguments.database_positional
    if not backup_name or not database_name:
        parser.print_help()
        return 2

    try:
        restore(backup_name, database_name)
    except (OSError, sqlite3.Error, ValueError):
        logger.exception("Test database restore failed")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
