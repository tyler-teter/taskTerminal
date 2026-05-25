from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from task_terminal.models import Task
from task_terminal.services.task_service import TaskService
from task_terminal.widgets.detail_panel import DetailPanel
from task_terminal.widgets.task_table import TaskTable


class MainScreen(Screen[None]):
    BINDINGS = [
        ("n", "new_task", "New"),
        ("e", "edit_task", "Edit"),
        ("d", "toggle_done", "Done/Undone"),
        ("v", "toggle_archived_visibility", "Show Completed"),
        ("slash", "search", "Search"),
        ("f", "filter", "Filter"),
        ("enter", "view_details", "Details"),
        ("question_mark", "help", "Help"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, service: TaskService) -> None:
        super().__init__()
        self.service = service
        self.tasks: list[Task] = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(
            "n:new e:edit d:done v:completed /:search f:filter Enter:details ?:help q:quit",
            id="helpbar",
        )
        with Horizontal(id="layout"):
            with Vertical(id="main-panel"):
                yield TaskTable(id="task-table")
            yield DetailPanel("No task selected", id="detail-panel")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_all()

    def refresh_all(self) -> None:
        self.service.default_project()
        self.tasks = self.service.tasks()
        table = self.query_one(TaskTable)
        table.load_tasks(self.tasks)
        self._sync_detail()

    def _sync_detail(self) -> None:
        table = self.query_one(TaskTable)
        detail = self.query_one(DetailPanel)
        task_id = table.selected_task_id()
        selected = next((t for t in self.tasks if t.id == task_id), None)
        detail.show_task(selected)

    def on_data_table_row_selected(self, _: TaskTable.RowSelected) -> None:
        self._sync_detail()

    def action_view_details(self) -> None:
        self._sync_detail()

    def action_new_task(self) -> None:
        self.app.push_screen("task_form")

    def action_edit_task(self) -> None:
        table = self.query_one(TaskTable)
        task_id = table.selected_task_id()
        if task_id is None:
            self.notify("Select a task first")
            return
        self.app.push_screen(("task_form", task_id))

    def action_toggle_done(self) -> None:
        table = self.query_one(TaskTable)
        task_id = table.selected_task_id()
        if task_id is None:
            self.notify("Select a task first")
            return
        self.service.toggle_done(task_id)
        self.refresh_all()

    def action_toggle_archived_visibility(self) -> None:
        showing = self.service.toggle_archived_visibility()
        state = "Showing" if showing else "Hiding"
        self.notify(f"{state} completed tasks")
        self.refresh_all()

    def action_search(self) -> None:
        self.app.push_screen("search")

    def action_filter(self) -> None:
        self.app.push_screen("filter")

    def action_help(self) -> None:
        self.app.push_screen("help")

    def action_quit(self) -> None:
        self.app.exit()
