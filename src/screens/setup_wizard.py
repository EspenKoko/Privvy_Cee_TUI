from pathlib import Path

from textual.screen import Screen
from textual.widgets import Header, Footer
from textual.app import ComposeResult

from src.widgets.add_host_widget import AddHostWidget
from src.widgets.add_server_widget import AddServerWidget
from src.widgets.polling_settings_widget import PollingSettingsWidget

SETUP_WIZARD_CSS = str(Path(__file__).resolve().parents[1] / "css" / "setup_wizard.tcss")


class AddHostScreen(Screen):
    """Add a hypervisor host machine."""

    CSS_PATH = SETUP_WIZARD_CSS

    def compose(self) -> ComposeResult:
        yield Header()
        yield AddHostWidget()
        yield Footer()


class AddServerScreen(Screen):
    """Add one server at a time; loops back to itself until user is done."""

    CSS_PATH = SETUP_WIZARD_CSS

    def compose(self) -> ComposeResult:
        yield Header()
        yield AddServerWidget()
        yield Footer()

class PollingSettingsScreen(Screen):
    CSS_PATH = SETUP_WIZARD_CSS

    def compose(self) -> ComposeResult:
        yield Header()
        yield PollingSettingsWidget()
        yield Footer()
