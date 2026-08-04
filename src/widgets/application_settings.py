from typing import Optional

from textual.containers import Vertical, Horizontal
from textual.widgets import Input, Button, Label, Static, Select
from textual.app import ComposeResult
from textual import on

from src.services.configuration import ConfigManager, AppSettings

class ApplicationSettings(Vertical):
    
    DEFAULT_CSS = """
    #app-settings-pane {
        border: solid $accent;
        padding: 1;
        height: auto;
    }

    DataTable {
        height: 1fr;
    }

    .field-label {
        margin-top: 1;
    }

    .button-row {
        margin-top: 1;
        height: auto;
    }

    .button-row Button {
        margin-right: 1;
    }
    
    #status-line {
        height: auto;
        margin-top: 1;
    }
    """
    
    def __init__(self) -> None:
        super().__init__()
        self.editing_server_name: Optional[str] = None  # None = "add new" mode

    def compose(self) -> ComposeResult:
        with Vertical(id="app-settings-pane"):
            yield Static("[b]Application Settings[/b]")
            with Horizontal():
                with Vertical():
                    yield Label("Polling rate (seconds)")
                    yield Input(id="settings-polling-rate")
                with Vertical():
                    yield Label("Theme")
                    yield Select(
                        [("Dark", "textual-dark"), ("Light", "textual-light")],
                        id="settings-theme",
                    )
                with Vertical():
                    yield Label("Log level")
                    yield Select(
                        [("DEBUG", "DEBUG"), ("INFO", "INFO"),
                            ("WARNING", "WARNING"), ("ERROR", "ERROR")],
                        id="settings-log-level",
                    )
            yield Button("Save Settings", id="save-app-settings-btn", variant="success")
            yield Static("", id="status-line")

    def on_mount(self) -> None:
        self._load_app_settings_into_form()
        
    def _load_app_settings_into_form(self) -> None:
        cfg_mgr: ConfigManager = self.app.config_manager
        settings = cfg_mgr.config.settings
        self.query_one("#settings-polling-rate", Input).value = str(settings.polling_rate_seconds)
        self.query_one("#settings-theme", Select).value = settings.theme
        self.query_one("#settings-log-level", Select).value = settings.log_level

    @on(Button.Pressed, "#save-app-settings-btn")
    def on_save_app_settings(self) -> None:
        cfg_mgr: ConfigManager = self.app.config_manager

        rate_raw = self.query_one("#settings-polling-rate", Input).value.strip()
        try:
            rate = int(rate_raw) if rate_raw else 5
        except ValueError:
            self._set_status("[red]Polling rate must be a number.[/red]")
            return

        theme = self.query_one("#settings-theme", Select).value
        log_level = self.query_one("#settings-log-level", Select).value

        cfg_mgr.config.settings = AppSettings(
            polling_rate_seconds=rate, theme=theme, log_level=log_level,
        )
        cfg_mgr.save()
        self._set_status("[green]Application settings saved.[/green]")

    def _set_status(self, message: str) -> None:
        self.query_one("#status-line", Static).update(message)