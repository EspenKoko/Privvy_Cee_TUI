from textual.screen import Screen
from textual.containers import Vertical
from textual.widgets import Header, Footer, Input, Button, Label, Static, Select
from textual.app import ComposeResult
from textual import on

from src.services.configuration import ConfigManager, AppSettings

class PollingSettingsScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="settings-box"):
            yield Static("Polling & display settings")
            yield Label("Polling rate (seconds)")
            yield Input(value="5", id="polling_rate")
            yield Label("Theme")
            yield Select(
                [("Dark", "textual-dark"), ("Light", "textual-light")],
                value="textual-dark",
                id="theme",
            )
            yield Button("Finish Setup", id="finish-btn", variant="success")
        yield Footer()

    @on(Button.Pressed, "#finish-btn")
    def finish_setup(self) -> None:
        cfg_mgr: ConfigManager = self.app.config_manager

        print(ConfigManager)
        rate = int(self.query_one("#polling_rate", Input).value or "5")
        theme = self.query_one("#theme", Select).value

        cfg_mgr.config.settings = AppSettings(polling_rate_seconds=rate, theme=theme)
        cfg_mgr.save()

        self.notify("Setup complete!")
        self.app.pop_screen()  # or push your main Dashboard screen instead