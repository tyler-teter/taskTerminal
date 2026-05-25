from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import DataTable

from task_terminal.models import Task


class TaskTable(DataTable):
    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.add_column("ID", width=4)
        self.add_column("Title", width=48)
        self.add_column("Status", width=8)
        self.add_column("Priority", width=8)
        self.add_column("Due", width=10)

    def load_tasks(self, tasks: list[Task]) -> None:
        self.clear(columns=False)
        for task in tasks:
            due = task.due_date or "-"
            self.add_row(str(task.id), task.title, task.status, task.priority, due)

    def selected_task_id(self) -> int | None:
        if self.cursor_row is None:
            return None
        try:
            row = self.get_row_at(self.cursor_row)
        except Exception:
            return None
        if not row:
            return None
        return int(str(row[0]))
