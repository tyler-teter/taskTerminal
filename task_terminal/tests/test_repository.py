from __future__ import annotations

from pathlib import Path

import pytest

from task_terminal.db import get_connection, init_db
from task_terminal.repository import ProjectRepository, TaskRepository, seed_data


@pytest.fixture()
def conn(tmp_path: Path):
    connection = get_connection(tmp_path / "test.db")
    init_db(connection)
    yield connection
    connection.close()


def test_seed_and_list_projects(conn):
    seed_data(conn)
    projects = ProjectRepository(conn).list_projects()
    assert len(projects) == 1
    assert projects[0].name == "Tasks"


def test_init_db_migrates_existing_projects_table(tmp_path: Path):
    connection = get_connection(tmp_path / "migration.db")
    connection.execute(
        """
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.commit()

    init_db(connection)

    columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(projects)").fetchall()
    }
    assert "archived_at" in columns
    connection.close()


def test_create_and_toggle_task(conn):
    project_repo = ProjectRepository(conn)
    task_repo = TaskRepository(conn)

    p = project_repo.create_project("Test", "desc")
    t = task_repo.create_task("hello", "world", p.id, "todo", "high")
    assert t.status == "todo"

    toggled = task_repo.toggle_done(t.id)
    assert toggled is not None
    assert toggled.status == "done"

    toggled2 = task_repo.toggle_done(t.id)
    assert toggled2 is not None
    assert toggled2.status == "todo"


def test_search_and_filter(conn):
    project_repo = ProjectRepository(conn)
    task_repo = TaskRepository(conn)

    p = project_repo.create_project("Search", "")
    task_repo.create_task("Alpha task", "contains unique token", p.id)
    task_repo.create_task("Beta task", "different", p.id, status="doing")

    found = task_repo.list_tasks(search="unique token")
    assert len(found) == 1
    assert found[0].title == "Alpha task"

    doing = task_repo.list_tasks(status="doing")
    assert any(t.title == "Beta task" for t in doing)


def test_ensure_default_project_merges_existing_projects(conn):
    project_repo = ProjectRepository(conn)
    task_repo = TaskRepository(conn)

    first = project_repo.create_project("First", "")
    second = project_repo.create_project("Second", "")
    task_repo.create_task("One", "", first.id)
    task_repo.create_task("Two", "", second.id)

    default = project_repo.ensure_default_project()

    assert default.name == "Tasks"
    assert [p.id for p in project_repo.list_projects(include_archived=True)] == [default.id]
    assert {t.project_id for t in task_repo.list_tasks(include_archived=True)} == {default.id}


def test_done_tasks_are_archived_by_completed_at(conn):
    project_repo = ProjectRepository(conn)
    task_repo = TaskRepository(conn)

    project = project_repo.ensure_default_project()
    visible = task_repo.create_task("Visible", "", project.id)
    hidden = task_repo.create_task("Hidden", "", project.id)
    completed = task_repo.toggle_done(hidden.id)

    assert [t.title for t in task_repo.list_tasks()] == ["Visible"]
    assert completed is not None
    assert completed.completed_at is not None
    assert {t.title for t in task_repo.list_tasks(include_archived=True)} == {"Visible", "Hidden"}

    reopened = task_repo.toggle_done(hidden.id)
    assert reopened is not None
    assert reopened.completed_at is None
    assert {t.id for t in task_repo.list_tasks()} == {visible.id, hidden.id}


def test_tasks_sort_by_due_date_before_priority(conn):
    project_repo = ProjectRepository(conn)
    task_repo = TaskRepository(conn)

    project = project_repo.ensure_default_project()
    task_repo.create_task("No date high", "", project.id, priority="high")
    task_repo.create_task("Later high", "", project.id, priority="high", due_date="2026-06-10")
    task_repo.create_task("Soon low", "", project.id, priority="low", due_date="2026-05-26")
    task_repo.create_task("Soon high", "", project.id, priority="high", due_date="2026-05-26")

    assert [t.title for t in task_repo.list_tasks(project_id=project.id)] == [
        "Soon high",
        "Soon low",
        "Later high",
        "No date high",
    ]
