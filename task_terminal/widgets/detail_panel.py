from __future__ import annotations

from textual.widgets import Static

from task_terminal.models import Task


class DetailPanel(Static):
    def show_task(self, task: Task | None) -> None:
        if not task:
            self.update("No task selected")
            return
        text = (
            f"[b]{task.title}[/b]\n"
            f"Status: {task.status}\n"
            f"Priority: {task.priority}\n"
            f"Due: {task.due_date or '-'}\n"
            f"Completed: {task.completed_at or '-'}\n\n"
            f"{task.description or '(no description)'}"
        )
        self.update(text)
