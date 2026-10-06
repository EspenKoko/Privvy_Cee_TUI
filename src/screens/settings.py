from __future__ import annotations

from pathlib import Path

from textual.screen import Screen
from textual.widgets import Header, Footer
from textual.app import ComposeResult
from textual.widgets import TabbedContent, TabPane
from textual.binding import Binding

from src.widgets.application_settings import ApplicationSettings
from src.widgets.server_settings import ServerConfiguration

class SettingsScreen(Screen):
    """
    Full settings screen: view/edit/delete servers, plus edit app-wide settings.
    Reachable via a keybinding (e.g. Ctrl+S) from the main app.
    """


    BINDINGS = [
            # Binding("escape", "cancel", "Cancel"),
            # Binding("d", "app.dashboard", "Dashboard", show=False, priority=True),
        ]

    CSS_PATH = str(Path(__file__).resolve().parents[1] / "css" / "settings_screen.tcss")
    
    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(id="settings-tabs"):
            with TabPane("Servers", id="tab-servers"):
                yield ServerConfiguration()
            with TabPane("App Settings", id="tab-app-settings"):
                yield ApplicationSettings()

        yield Footer()