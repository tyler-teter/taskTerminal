from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class HelpScreen(ModalScreen[None]):
    def compose(self) -> ComposeResult:
        with Vertical(id="help-modal"):
            yield Static(
                "Keyboard shortcuts\n"
                "n New task\n"
                "e Edit task\n"
                "d Toggle done and archive\n"
                "v Show/hide completed tasks\n"
                "/ Search\n"
                "f Filter status\n"
                "Arrow keys Navigate\n"
                "Enter View details\n"
                "q Quit\n"
            )
            yield Button("Close", id="close", variant="primary")

    def on_button_pressed(self, _: Button.Pressed) -> None:
        self.dismiss()
