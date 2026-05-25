from __future__ import annotations

from textual.app import App

from task_terminal.db import get_connection, init_db
from task_terminal.repository import ProjectRepository, TaskRepository, seed_data
from task_terminal.screens.help import HelpScreen
from task_terminal.screens.main import MainScreen
from task_terminal.screens.task_form import PromptScreen, TaskFormScreen
from task_terminal.services.task_service import TaskService


class TaskTerminalApp(App[None]):
    CSS = """
    #layout { height: 1fr; }
    #project-sidebar { width: 28; border: round $panel; }
    #main-panel { width: 1fr; border: round $panel; }
    #detail-panel { width: 40; border: round $panel; padding: 1; }
    #helpbar { dock: top; background: $accent; color: $text; padding: 0 1; }
    #task-form, #help-modal, #prompt-box, #project-form { width: 70; height: auto; border: round $panel; padding: 1 2; background: $surface; }
    """

    def on_mount(self) -> None:
        conn = get_connection()
        init_db(conn)
        seed_data(conn)

        self.project_repo = ProjectRepository(conn)
        self.task_repo = TaskRepository(conn)
        self.service = TaskService(self.project_repo, self.task_repo)

        self.install_screen(MainScreen(self.service), "main")
        self.install_screen(HelpScreen(), "help")
        self.install_screen(TaskFormScreen(self.service), "task_form")
        self.install_screen(PromptScreen("Search tasks", "title or description"), "search")
        self.install_screen(PromptScreen("Filter status: all|todo|doing|done", "all"), "filter")

        self.push_screen("main")

    def push_screen(self, screen, callback=None, wait_for_dismiss=False):  # type: ignore[override]
        if screen == "task_form":
            return super().push_screen(TaskFormScreen(self.service), self._after_mutation)
        if isinstance(screen, tuple) and screen[0] == "task_form":
            return super().push_screen(TaskFormScreen(self.service, task_id=screen[1]), self._after_mutation)
        if screen == "search":
            return super().push_screen(PromptScreen("Search tasks", "title or description"), self._after_search)
        if screen == "filter":
            return super().push_screen(PromptScreen("Filter status: all|todo|doing|done", "all"), self._after_filter)
        return super().push_screen(screen, callback, wait_for_dismiss)

    def _after_mutation(self, _: object) -> None:
        main = self.get_screen("main")
        main.refresh_all()

    def _after_search(self, value: str | None) -> None:
        if value is not None:
            self.service.set_search(value)
            self.get_screen("main").refresh_all()

    def _after_filter(self, value: str | None) -> None:
        if value is None:
            return
        normalized = value.strip().lower() or "all"
        if normalized not in {"all", "todo", "doing", "done"}:
            self.notify("Filter must be all/todo/doing/done")
            return
        self.service.set_status_filter(normalized)
        self.get_screen("main").refresh_all()
