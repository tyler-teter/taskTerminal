from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from task_terminal.models import Project, Task
from task_terminal.repository import ProjectRepository, TaskRepository


@dataclass(slots=True)
class TaskFilters:
    search: str = ""
    status: str = "all"
    project_id: Optional[int] = None
    include_archived_tasks: bool = False


class TaskService:
    def __init__(self, project_repo: ProjectRepository, task_repo: TaskRepository) -> None:
        self.project_repo = project_repo
        self.task_repo = task_repo
        self.filters = TaskFilters()

    def projects(self) -> list[Project]:
        return self.project_repo.list_projects()

    def default_project(self) -> Project:
        return self.project_repo.ensure_default_project()

    def tasks(self) -> list[Task]:
        return self.task_repo.list_tasks(
            project_id=self.filters.project_id,
            search=self.filters.search,
            status=self.filters.status,
            include_archived=self.filters.include_archived_tasks,
        )

    def set_search(self, query: str) -> None:
        self.filters.search = query.strip()

    def set_status_filter(self, status: str) -> None:
        self.filters.status = status

    def set_project(self, project_id: Optional[int]) -> None:
        self.filters.project_id = project_id

    def toggle_archived_visibility(self) -> bool:
        self.filters.include_archived_tasks = not self.filters.include_archived_tasks
        return self.filters.include_archived_tasks

    def normalize_due_date(self, due_date: Optional[str]) -> Optional[str]:
        if due_date is None or not due_date.strip():
            return None

        raw = due_date.strip()
        for date_format in ("%Y-%m-%d", "%m-%d-%Y", "%m/%d/%Y"):
            try:
                return datetime.strptime(raw, date_format).date().isoformat()
            except ValueError:
                continue
        raise ValueError("Due date must be YYYY-MM-DD, MM-DD-YYYY, or MM/DD/YYYY")

    def create_task(
        self,
        title: str,
        description: str,
        project_id: int,
        status: str,
        priority: str,
        due_date: Optional[str] = None,
    ) -> Task:
        project_id = self.default_project().id
        due_date = self.normalize_due_date(due_date)
        return self.task_repo.create_task(title, description, project_id, status, priority, due_date)

    def update_task(
        self,
        task_id: int,
        title: str,
        description: str,
        status: str,
        priority: str,
        project_id: int,
        due_date: Optional[str] = None,
    ) -> Optional[Task]:
        project_id = self.default_project().id
        due_date = self.normalize_due_date(due_date)
        return self.task_repo.update_task(
            task_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            project_id=project_id,
            due_date=due_date,
        )

    def toggle_done(self, task_id: int) -> Optional[Task]:
        return self.task_repo.toggle_done(task_id)
