from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, TextArea

from task_terminal.models import TASK_PRIORITIES, TASK_STATUSES
from task_terminal.services.task_service import TaskService


class TaskFormScreen(ModalScreen[None]):
    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, service: TaskService, task_id: int | None = None) -> None:
        super().__init__()
        self.service = service
        self.task_id = task_id

    def compose(self) -> ComposeResult:
        with Vertical(id="task-form"):
            yield Label("Task Form")
            yield Input(placeholder="Title", id="title")
            yield TextArea(id="description")
            yield Select([(s, s) for s in TASK_STATUSES], value="todo", id="status")
            yield Select([(p, p) for p in TASK_PRIORITIES], value="normal", id="priority")
            yield Input(placeholder="Due date (YYYY-MM-DD)", id="due_date")
            yield Button("Save", id="save", variant="success")
            yield Button("Cancel", id="cancel")

    def on_mount(self) -> None:
        if self.task_id is None:
            return
        task = self.service.task_repo.get_task(self.task_id)
        if not task:
            return
        self.query_one("#title", Input).value = task.title
        self.query_one("#description", TextArea).text = task.description
        self.query_one("#status", Select).value = task.status
        self.query_one("#priority", Select).value = task.priority
        self.query_one("#due_date", Input).value = task.due_date or ""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss()
            return

        title = self.query_one("#title", Input).value
        description = self.query_one("#description", TextArea).text
        status = str(self.query_one("#status", Select).value)
        priority = str(self.query_one("#priority", Select).value)
        project_id = self.service.default_project().id
        due_date = self.query_one("#due_date", Input).value.strip() or None

        try:
            if self.task_id is None:
                self.service.create_task(title, description, project_id, status, priority, due_date)
            else:
                self.service.update_task(self.task_id, title, description, status, priority, project_id, due_date)
        except ValueError as exc:
            self.notify(str(exc))
            return
        self.dismiss()

    def action_cancel(self) -> None:
        self.dismiss()


class PromptScreen(ModalScreen[str | None]):
    def __init__(self, title: str, placeholder: str = "") -> None:
        super().__init__()
        self.title = title
        self.placeholder = placeholder

    def compose(self) -> ComposeResult:
        with Vertical(id="prompt-box"):
            yield Label(self.title)
            yield Input(placeholder=self.placeholder, id="prompt-input")
            yield Button("Apply", id="apply", variant="success")
            yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
            return
        self.dismiss(self.query_one("#prompt-input", Input).value)
