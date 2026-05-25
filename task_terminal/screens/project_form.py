from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, TextArea

from task_terminal.repository import ProjectRepository


class ProjectFormScreen(ModalScreen[None]):
    def __init__(self, project_repo: ProjectRepository) -> None:
        super().__init__()
        self.project_repo = project_repo

    def compose(self) -> ComposeResult:
        with Vertical(id="project-form"):
            yield Label("New Project")
            yield Input(placeholder="Project name", id="name")
            yield TextArea(id="description")
            yield Button("Save", id="save", variant="success")
            yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss()
            return
        name = self.query_one("#name", Input).value
        description = self.query_one("#description", TextArea).text
        if name.strip():
            self.project_repo.create_project(name, description)
        self.dismiss()
