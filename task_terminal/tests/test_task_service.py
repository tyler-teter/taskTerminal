from __future__ import annotations

from pathlib import Path

import pytest

from task_terminal.db import get_connection, init_db
from task_terminal.repository import ProjectRepository, TaskRepository
from task_terminal.services.task_service import TaskService


@pytest.fixture()
def service(tmp_path: Path):
    conn = get_connection(tmp_path / "service.db")
    init_db(conn)
    projects = ProjectRepository(conn)
    tasks = TaskRepository(conn)
    svc = TaskService(projects, tasks)
    default = svc.default_project()
    yield svc, default.id
    conn.close()


def test_service_create_and_query(service):
    svc, project_id = service
    svc.create_task("Test Task", "Body", project_id, "todo", "normal")
    rows = svc.tasks()
    assert len(rows) == 1
    assert rows[0].title == "Test Task"


def test_service_filters(service):
    svc, project_id = service
    svc.create_task("One", "aaa", project_id, "todo", "normal")
    svc.create_task("Two", "bbb", project_id, "doing", "high")

    svc.set_status_filter("doing")
    rows = svc.tasks()
    assert len(rows) == 1
    assert rows[0].title == "Two"

    svc.set_status_filter("all")
    svc.set_search("aaa")
    rows = svc.tasks()
    assert len(rows) == 1
    assert rows[0].title == "One"


def test_service_normalizes_due_date_formats(service):
    svc, project_id = service

    first = svc.create_task("ISO", "", project_id, "todo", "normal", "2026-05-26")
    second = svc.create_task("US", "", project_id, "todo", "normal", "05-27-2026")
    third = svc.create_task("US slash", "", project_id, "todo", "normal", "05/28/2026")

    assert first.due_date == "2026-05-26"
    assert second.due_date == "2026-05-27"
    assert third.due_date == "2026-05-28"

    updated = svc.update_task(first.id, "ISO", "", "todo", "normal", project_id, "06-01-2026")
    assert updated is not None
    assert updated.due_date == "2026-06-01"


def test_service_rejects_invalid_due_date(service):
    svc, project_id = service

    with pytest.raises(ValueError, match="Due date"):
        svc.create_task("Bad date", "", project_id, "todo", "normal", "13-40-2026")


def test_service_archive_visibility_and_selected_project_reset(service):
    svc, project_id = service
    svc.create_task("Archived task", "", project_id, "todo", "normal")

    task = svc.tasks()[0]
    archived = svc.toggle_done(task.id)
    assert archived is not None
    assert archived.completed_at is not None
    assert [p.id for p in svc.projects()] == [project_id]
    assert svc.tasks() == []

    assert svc.toggle_archived_visibility() is True
    assert [t.title for t in svc.tasks()] == ["Archived task"]

    restored = svc.toggle_done(task.id)
    assert restored is not None
    assert restored.completed_at is None
