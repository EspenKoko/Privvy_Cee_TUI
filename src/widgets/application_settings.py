from pathlib import Path
from typing import Optional

from textual.containers import Vertical, Horizontal
from textual.widgets import Input, Button, Label, Static, Select
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual import on

from src.screens.welcome import WelcomeScreen
from src.services.configuration import ConfigManager, AppSettings
from src.services.token_store import TokenStore
from src.widgets.host_Panel import HostPanel
from src.widgets.host_Panel_details import HostPanelDetails
from src.widgets.server_panel import ServerPanel


class ConfirmDeleteDataScreen(ModalScreen[Optional[bool]]):
    DEFAULT_CSS = """
    ConfirmDeleteDataScreen {
        align: center middle;
    }

    #delete-confirmation {
        width: 60;
        height: auto;
        padding: 1 2;
        border: thick $error;
        background: $surface;
    }

    #delete-confirmation-buttons {
        height: auto;
        margin-top: 1;
        align-horizontal: right;
    }

    #delete-confirmation-buttons Button {
        margin-left: 1;
    }
    """
    
    def compose(self) -> ComposeResult:
        with Vertical(id="delete-confirmation"):
            yield Static("[b]Delete all saved data?[/b]")
            yield Static(
                "This removes config.toml and the app's saved Windows credentials. "
                "This action cannot be undone."
            )
            with Horizontal(id="delete-confirmation-buttons"):
                yield Button("Cancel", id="cancel-delete-data")
                yield Button("Delete", id="confirm-delete-data", variant="error")

    @on(Button.Pressed, "#cancel-delete-data")
    def cancel_delete(self) -> None:
        self.dismiss(False)

    @on(Button.Pressed, "#confirm-delete-data")
    def confirm_delete(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)


class ApplicationSettings(Vertical):
    _css_path = Path(__file__).resolve().parents[1] / "css" / "application_settings.tcss"
    DEFAULT_CSS = _css_path.read_text(encoding="utf-8")
    
    def __init__(self) -> None:
        super().__init__()
        self.editing_server_name: Optional[str] = None  # None = "add new" mode

    def compose(self) -> ComposeResult:
        with Vertical(id="app-settings-pane"):
            yield Static("[b]Application Settings[/b]", id="header")
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
            with Horizontal():
                with Vertical():
                    yield Label("Secure app with Login")
                    yield Select(
                        [("Yes", "yes"), ("No", "no")],
                        id="settings-login",
                    )
            with Horizontal():
                yield Button("Save Settings", id="save-app-settings-btn", variant="success")
                yield Button("Delete All Data", id="data-deletion-btn", variant="error")
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
        for screen in self.app.screen_stack:
            for servers_tab in screen.query(ServerPanel):
                servers_tab.update_polling_interval()
        self._set_status("[green]Application settings saved.[/green]")

    @on(Button.Pressed, "#data-deletion-btn")
    def on_delete_all_data(self) -> None:
        self.app.push_screen(ConfirmDeleteDataScreen(), self._on_delete_confirmation)

    def _on_delete_confirmation(self, confirmed: Optional[bool]) -> None:
        if not confirmed:
            return

        cfg_mgr: ConfigManager = self.app.config_manager
        try:
            self._stop_dashboard_polling()
            TokenStore().delete_token()
            cfg_mgr.delete_all_data()
        except Exception:
            self._set_status(
                "[red]Could not delete all data. Check credential store permissions.[/red]"
            )
            return

        self._load_app_settings_into_form()
        self._set_status("[green]All saved data and credentials were deleted.[/green]")

    def _stop_dashboard_polling(self) -> None:
        poller_types = (HostPanel, HostPanelDetails, ServerPanel)
        for screen in self.app.screen_stack:
            for poller_type in poller_types:
                for poller in screen.query(poller_type):
                    poller.stop_polling()
        self.app.push_screen(WelcomeScreen())
        

    def _set_status(self, message: str) -> None:
        self.query_one("#status-line", Static).update(message)