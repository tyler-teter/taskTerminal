from __future__ import annotations

from textual.widgets import ListItem, ListView, Static

from task_terminal.models import Project


class ProjectSidebar(ListView):
    def load_projects(self, projects: list[Project], selected_id: int | None = None) -> None:
        self.clear()
        all_projects = ListItem(Static("All Projects"))
        all_projects.project_id = None
        all_projects.project_archived = False
        self.append(all_projects)
        for project in projects:
            label = f"[archived] {project.name}" if project.archived_at else project.name
            item = ListItem(Static(label))
            item.project_id = project.id
            item.project_archived = project.archived_at is not None
            self.append(item)

        target_index = 0
        if selected_id is not None:
            for idx, child in enumerate(self.children):
                if getattr(child, "project_id", None) == selected_id:
                    target_index = idx
                    break
        self.index = target_index

    def current_project_id(self) -> int | None:
        if self.index is None:
            return None
        item = self.children[self.index]
        return getattr(item, "project_id", None)

    def current_project_archived(self) -> bool:
        if self.index is None:
            return False
        item = self.children[self.index]
        return bool(getattr(item, "project_archived", False))
