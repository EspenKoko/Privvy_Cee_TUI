from __future__ import annotations

from textual.screen import Screen
from textual.widgets import Header, Footer
from textual.app import ComposeResult

from src.widgets.application_settings import ApplicationSettings
from src.widgets.server_settings import ServerConfiguration
from textual.widgets import TabbedContent, TabPane

class SettingsScreen(Screen):
    """
    Full settings screen: view/edit/delete servers, plus edit app-wide settings.
    Reachable via a keybinding (e.g. Ctrl+S) from the main app.
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
    ]

    DEFAULT_CSS = """
    SettingsScreen {
        layout: vertical;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(id="settings-tabs"):
            with TabPane("Servers", id="tab-servers"):
                yield ServerConfiguration()
                        
            with TabPane("App Settings", id="tab-app-settings"):
                yield ApplicationSettings()

        yield Footer()