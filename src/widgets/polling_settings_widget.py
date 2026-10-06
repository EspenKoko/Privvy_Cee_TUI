from textual import on
from textual.app import ComposeResult
from textual.containers import Center, Vertical, VerticalScroll
from textual.widget import Widget
from textual.widgets import Button, Input, Label, Select

from src.services.configuration import AppSettings, ConfigManager


class PollingSettingsWidget(Widget):
    def compose(self) -> ComposeResult:
        with Center(id="polling-settings-container"):
            with Vertical(id="polling-settings-content"):
                yield Label("3/3 - Polling & Display Settings", id="polling-settings-title")
                with VerticalScroll(id="settings-box"):
                    yield Label("Polling rate (seconds)")
                    yield Input(value="5", id="polling_rate")
                    yield Label("Theme")
                    yield Select(
                        [("Dark", "textual-dark"), ("Light", "textual-light")],
                        value="textual-dark",
                        id="theme",
                    )
                    yield Button("Finish Setup", id="finish-btn", variant="success")
                    yield Button("Return", id="back-btn")

    @on(Button.Pressed, "#back-btn")
    def _return(self) -> None:
        from src.screens.setup_wizard import AddServerScreen

        self.app.push_screen(AddServerScreen())

    @on(Button.Pressed, "#finish-btn")
    def finish_setup(self) -> None:
        cfg_mgr: ConfigManager = self.app.config_manager

        print(ConfigManager)
        rate = int(self.query_one("#polling_rate", Input).value or "5")
        theme = self.query_one("#theme", Select).value

        cfg_mgr.config.settings = AppSettings(polling_rate_seconds=rate, theme=theme)
        cfg_mgr.save()

        self.notify("Setup complete!")
        from src.screens.dashboard import DashboardScreen

        self.app.push_screen(DashboardScreen())