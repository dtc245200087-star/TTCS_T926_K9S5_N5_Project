"""Persistence helpers for projects and their hierarchical work items."""

import sqlite3
from contextlib import closing


def _connect(database_path):
    db = sqlite3.connect(database_path, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def _required_name(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def create_project(database_path, name):
    name = _required_name(name, "Project name")
    with closing(_connect(database_path)) as db:
        cursor = db.execute("INSERT INTO projects (name) VALUES (?)", (name,))
        db.commit()
        row = db.execute(
            "SELECT id, name, created_at FROM projects WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
        return dict(row)


def create_work_item(database_path, project_id, name, parent_id=None):
    name = _required_name(name, "Work item name")
    with closing(_connect(database_path)) as db:
        cursor = db.execute(
            """INSERT INTO work_items (project_id, parent_id, name)
               VALUES (?, ?, ?)""",
            (project_id, parent_id, name),
        )
        db.commit()
        row = db.execute(
            """SELECT id, project_id, parent_id, name, created_at
               FROM work_items WHERE id = ?""",
            (cursor.lastrowid,),
        ).fetchone()
        return dict(row)


def get_work_item_tree(database_path, work_item_id):
    """Return the requested work item and every descendant as a nested tree."""
    with closing(_connect(database_path)) as db:
        rows = db.execute(
            """WITH RECURSIVE subtree(
                   id, project_id, parent_id, name, created_at, depth, path
               ) AS (
                   SELECT id, project_id, parent_id, name, created_at, 0,
                          printf('/%d/', id)
                   FROM work_items
                   WHERE id = ?
                   UNION ALL
                   SELECT child.id, child.project_id, child.parent_id, child.name,
                          child.created_at, parent.depth + 1,
                          parent.path || printf('%d/', child.id)
                   FROM work_items child
                   JOIN subtree parent ON child.parent_id = parent.id
                   WHERE instr(parent.path, printf('/%d/', child.id)) = 0
               )
               SELECT id, project_id, parent_id, name, created_at, depth
               FROM subtree
               ORDER BY depth, id""",
            (work_item_id,),
        ).fetchall()

    if not rows:
        return None

    nodes = {}
    for row in rows:
        node = {
            "id": row["id"],
            "project_id": row["project_id"],
            "parent_id": row["parent_id"],
            "name": row["name"],
            "created_at": row["created_at"],
            "children": [],
        }
        nodes[node["id"]] = node
        if row["depth"] > 0:
            nodes[row["parent_id"]]["children"].append(node)
    return nodes[rows[0]["id"]]
