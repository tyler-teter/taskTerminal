from __future__ import annotations

import sqlite3
import os
from pathlib import Path

DEFAULT_DB_PATH = Path(os.environ.get("TASK_TERMINAL_DB", Path.home() / ".task_terminal.db"))


def get_connection(db_path: str | Path | None = None) -> sqlite3.Connection:
    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            archived_at TEXT
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL CHECK(status IN ('todo', 'doing', 'done')) DEFAULT 'todo',
            priority TEXT NOT NULL CHECK(priority IN ('low', 'normal', 'high')) DEFAULT 'normal',
            project_id INTEGER NOT NULL,
            due_date TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            completed_at TEXT,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks(project_id);
        CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
        CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
        """
    )
    columns = {
        row["name"]
        for row in conn.execute("PRAGMA table_info(projects)").fetchall()
    }
    if "archived_at" not in columns:
        conn.execute("ALTER TABLE projects ADD COLUMN archived_at TEXT")
    conn.commit()
