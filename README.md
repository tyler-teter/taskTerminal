# Task Terminal

Keyboard-friendly terminal task manager built with Textual + SQLite.

## Features
- Task table with status/priority/due date
- Task detail panel
- Visible top help bar
- Keyboard shortcuts (`n`, `e`, `d`, `/`, `f`, `v`, `q`, `?`, arrows, Enter)
- Completed tasks are archived automatically with their completion timestamp
- Show or hide completed tasks with `v`
- SQLite local persistence with seed data
- Search and status filter
- Tasks sorted by soonest due date first
- Due dates accept `YYYY-MM-DD`, `MM-DD-YYYY`, or `MM/DD/YYYY`, and display as `YYYY-MM-DD`

## One-click launch (Windows)
- Double-click `Launch Task Terminal.bat` from this folder.
- It uses `uv` to install/use Python 3.12, verify `sqlite3`, install requirements in an isolated environment, and start the app.
- If `uv` is missing, the launcher installs it with the official Astral Windows installer.

### Add to Start Menu and Desktop
- After the first successful run, the launcher asks once whether to install Start Menu and Desktop shortcuts.
- Choose `Y` to register **Task Terminal** in Windows so it appears in the Apps list and Start search; from then on you can launch it by typing "Task Terminal" into Start.
- To pin to the taskbar, right-click the Start Menu entry and choose **Pin to taskbar**.
- The shortcuts point at this folder. If you move the repo, delete the old shortcuts and delete `.shortcuts-offered` so the launcher offers to recreate them on the next run.

## Install (manual)
```bash
uv python install 3.12
uv run --python 3.12 --with-requirements requirements.txt python -m task_terminal
```

## Run (manual)
```bash
uv run --python 3.12 --with-requirements requirements.txt python -m task_terminal
```

## Tests
```bash
uv run --python 3.12 --with-requirements requirements.txt pytest task_terminal/tests -q
```

## Structure
- `task_terminal/db.py`: SQLite connection + schema
- `task_terminal/models.py`: dataclass models
- `task_terminal/repository.py`: DB CRUD + seed data
- `task_terminal/services/task_service.py`: business/state filters
- `task_terminal/screens/*`: main and modal screens
- `task_terminal/widgets/*`: table and detail panel widgets
- `task_terminal/app.py`: Textual app wiring

## Notes
- Database file defaults to `~/.task_terminal.db`.
- Set `TASK_TERMINAL_DB` to choose a different database path.
- Status values: `todo`, `doing`, `done`.
- Priority values: `low`, `normal`, `high`.
- Due dates are stored and shown as `YYYY-MM-DD`.
