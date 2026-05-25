from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

TASK_STATUSES = ("todo", "doing", "done")
TASK_PRIORITIES = ("low", "normal", "high")


@dataclass(slots=True)
class Project:
    id: int
    name: str
    description: str
    created_at: datetime
    archived_at: Optional[datetime]


@dataclass(slots=True)
class Task:
    id: int
    title: str
    description: str
    status: str
    priority: str
    project_id: int
    due_date: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
