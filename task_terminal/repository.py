from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Optional

from task_terminal.models import Project, Task, TASK_PRIORITIES, TASK_STATUSES

DEFAULT_PROJECT_NAME = "Tasks"


def _project_from_row(row: sqlite3.Row) -> Project:
    return Project(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        created_at=datetime.fromisoformat(row["created_at"]),
        archived_at=datetime.fromisoformat(row["archived_at"])
        if row["archived_at"]
        else None,
    )


class ProjectRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def list_projects(self, include_archived: bool = False) -> list[Project]:
        query = "SELECT id, name, description, created_at, archived_at FROM projects"
        if not include_archived:
            query += " WHERE archived_at IS NULL"
        query += " ORDER BY archived_at IS NOT NULL, name"
        rows = self.conn.execute(query).fetchall()
        return [_project_from_row(row) for row in rows]

    def create_project(self, name: str, description: str = "") -> Project:
        cur = self.conn.execute(
            "INSERT INTO projects(name, description) VALUES(?, ?)",
            (name.strip(), description.strip()),
        )
        self.conn.commit()
        row = self.conn.execute(
            "SELECT id, name, description, created_at, archived_at FROM projects WHERE id = ?",
            (cur.lastrowid,),
        ).fetchone()
        return _project_from_row(row)

    def ensure_default_project(self) -> Project:
        row = self.conn.execute(
            "SELECT id, name, description, created_at, archived_at FROM projects WHERE name = ?",
            (DEFAULT_PROJECT_NAME,),
        ).fetchone()
        if row:
            project = _project_from_row(row)
        else:
            project = self.create_project(DEFAULT_PROJECT_NAME, "Default task list")

        self.conn.execute(
            "UPDATE tasks SET project_id = ? WHERE project_id != ?",
            (project.id, project.id),
        )
        self.conn.execute("DELETE FROM projects WHERE id != ?", (project.id,))
        self.conn.execute("UPDATE projects SET archived_at = NULL WHERE id = ?", (project.id,))
        self.conn.commit()
        return self.get_project(project.id) or project

    def get_project(self, project_id: int) -> Optional[Project]:
        row = self.conn.execute(
            "SELECT id, name, description, created_at, archived_at FROM projects WHERE id = ?",
            (project_id,),
        ).fetchone()
        return _project_from_row(row) if row else None

    def archive_project(self, project_id: int) -> Optional[Project]:
        self.conn.execute(
            "UPDATE projects SET archived_at = CURRENT_TIMESTAMP WHERE id = ?",
            (project_id,),
        )
        self.conn.commit()
        return self.get_project(project_id)

    def restore_project(self, project_id: int) -> Optional[Project]:
        self.conn.execute(
            "UPDATE projects SET archived_at = NULL WHERE id = ?",
            (project_id,),
        )
        self.conn.commit()
        return self.get_project(project_id)

    def toggle_project_archive(self, project_id: int) -> Optional[Project]:
        project = self.get_project(project_id)
        if not project:
            return None
        if project.archived_at:
            return self.restore_project(project_id)
        return self.archive_project(project_id)


class TaskRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def list_tasks(
        self,
        project_id: Optional[int] = None,
        search: str = "",
        status: str = "all",
        include_archived: bool = False,
    ) -> list[Task]:
        query = """
            SELECT id, title, description, status, priority, project_id, due_date,
                   created_at, updated_at, completed_at
            FROM tasks
            WHERE 1=1
        """
        params: list[object] = []
        if project_id:
            query += " AND project_id = ?"
            params.append(project_id)
        if not include_archived:
            query += " AND completed_at IS NULL"
        if search:
            query += " AND (title LIKE ? OR description LIKE ?)"
            q = f"%{search}%"
            params.extend([q, q])
        if status in TASK_STATUSES:
            query += " AND status = ?"
            params.append(status)
        query += """
            ORDER BY due_date IS NULL,
                     due_date,
                     CASE priority WHEN 'high' THEN 1 WHEN 'normal' THEN 2 ELSE 3 END,
                     updated_at DESC
        """

        rows = self.conn.execute(query, params).fetchall()
        tasks: list[Task] = []
        for row in rows:
            tasks.append(
                Task(
                    id=row["id"],
                    title=row["title"],
                    description=row["description"],
                    status=row["status"],
                    priority=row["priority"],
                    project_id=row["project_id"],
                    due_date=row["due_date"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                    completed_at=datetime.fromisoformat(row["completed_at"])
                    if row["completed_at"]
                    else None,
                )
            )
        return tasks

    def get_task(self, task_id: int) -> Optional[Task]:
        row = self.conn.execute(
            """
            SELECT id, title, description, status, priority, project_id, due_date,
                   created_at, updated_at, completed_at
            FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        ).fetchone()
        if not row:
            return None
        return Task(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            status=row["status"],
            priority=row["priority"],
            project_id=row["project_id"],
            due_date=row["due_date"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            completed_at=datetime.fromisoformat(row["completed_at"])
            if row["completed_at"]
            else None,
        )

    def create_task(
        self,
        title: str,
        description: str,
        project_id: int,
        status: str = "todo",
        priority: str = "normal",
        due_date: Optional[str] = None,
    ) -> Task:
        if status not in TASK_STATUSES:
            raise ValueError(f"invalid status: {status}")
        if priority not in TASK_PRIORITIES:
            raise ValueError(f"invalid priority: {priority}")

        cur = self.conn.execute(
            """
            INSERT INTO tasks(title, description, status, priority, project_id, due_date)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            (title.strip(), description.strip(), status, priority, project_id, due_date),
        )
        self.conn.commit()
        task = self.get_task(cur.lastrowid)
        if not task:
            raise RuntimeError("task creation failed")
        return task

    def update_task(
        self,
        task_id: int,
        *,
        title: str,
        description: str,
        status: str,
        priority: str,
        project_id: int,
        due_date: Optional[str],
    ) -> Optional[Task]:
        if status not in TASK_STATUSES:
            raise ValueError(f"invalid status: {status}")
        if priority not in TASK_PRIORITIES:
            raise ValueError(f"invalid priority: {priority}")

        current = self.get_task(task_id)
        if status == "done":
            completed_at = (
                current.completed_at.isoformat(timespec="seconds")
                if current and current.completed_at
                else datetime.now().isoformat(timespec="seconds")
            )
        else:
            completed_at = None

        self.conn.execute(
            """
            UPDATE tasks
            SET title=?, description=?, status=?, priority=?, project_id=?, due_date=?,
                updated_at=CURRENT_TIMESTAMP, completed_at=?
            WHERE id=?
            """,
            (
                title.strip(),
                description.strip(),
                status,
                priority,
                project_id,
                due_date,
                completed_at,
                task_id,
            ),
        )
        self.conn.commit()
        return self.get_task(task_id)

    def toggle_done(self, task_id: int) -> Optional[Task]:
        task = self.get_task(task_id)
        if not task:
            return None
        new_status = "todo" if task.status == "done" else "done"
        completed_at = datetime.now().isoformat(timespec="seconds") if new_status == "done" else None
        self.conn.execute(
            """
            UPDATE tasks
            SET status=?, completed_at=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
            """,
            (new_status, completed_at, task_id),
        )
        self.conn.commit()
        return self.get_task(task_id)


def seed_data(conn: sqlite3.Connection) -> None:
    project_repo = ProjectRepository(conn)
    default = project_repo.ensure_default_project()

    task_count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    if task_count > 0:
        return

    task_repo = TaskRepository(conn)

    task_repo.create_task("Review pull requests", "Check pending repo PRs", default.id, "doing", "high")
    task_repo.create_task("Buy groceries", "Milk, eggs, and coffee", default.id, "todo", "normal")
    task_repo.create_task("Plan week", "Set goals for this week", default.id, "todo", "low")
