from textual.screen import Screen
from textual.containers import Vertical, Horizontal
from textual.widgets import (
    Header,
    Footer,
    Input,
    Button,
    Label,
    Static,
    Select,
    Checkbox,
    RadioButton,
    RadioSet,
)
from textual.app import ComposeResult
from textual import on, work
from typing import Optional

from src.services.configuration import ConfigManager, ServerConfig, AppSettings
from src.screens.dashboard import DashboardScreen
from src.api.pve_access_ticket import PVEAuthentivation


class WelcomeScreen(Screen):
    """First screen shown on a fresh install."""

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="welcome-box"):
            yield Static("👋 Welcome to Privvy_Cee_TUI", id="welcome-title")
            yield Static(
                "Looks like this is your first run. Let's set up your environemnt "
            )
            yield Button("Get Started", id="start-btn", variant="primary")
        yield Footer()

    @on(Button.Pressed, "#start-btn")
    def start_setup(self) -> None:
        self.app.push_screen(AddHostScreen())


class AddHostScreen(Screen):
    """Add a hypervisor host machine."""

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="add-host-box"):
            yield Label("Host Name")
            yield Input(placeholder="e.g. Dragon warrior", id="name", tooltip="Match casing of the host's name")
            yield Label("Host IP address")
            yield Input(placeholder="192.168.1.15", id="address")
            yield Label("Port")
            yield Input(placeholder="22", value="22", id="port")
            yield Label("Username")
            yield Input(placeholder="root", id="username")
            yield Label("Auth method")
            yield Select(
                [("Password", "password"), ("SSH Key", "ssh_key")],
                value="password",
                id="auth_method",
            )
            yield Label("Password (stored securely in your OS keyring, not this file)")
            yield Input(placeholder="", password=True, id="password")
            yield Label("SSH key path (only if using SSH Key auth)")
            yield Input(placeholder="~/.ssh/id_ed25519", id="ssh_key_path")
            yield Checkbox("Using a host e.g. proxmox", id="hypervisorCheck", value=False)
            hypervisor_label = Label("Hypervisor type", id="hypervisor-label")
            hypervisor_label.display = False
            yield hypervisor_label
            hypervisor_options = RadioSet(
                RadioButton("Proxmox", id="proxmox-option"),
                RadioButton("Other", id="other-hypervisor-option"),
                id="hypervisor-options",
            )
            hypervisor_options.display = False
            yield hypervisor_options
                
            with Horizontal():
                yield Button("Add Host", id="add-btn", variant="primary")
                # TODO add loding indicator when this button is clicked
                # yield Button("Done — Continue", id="done-btn")
        yield Footer()

    @on(Checkbox.Changed, "#hypervisorCheck")
    def toggle_hypervisor_options(self, event: Checkbox.Changed) -> None:
        self.query_one("#hypervisor-label", Label).display = event.value
        self.query_one("#hypervisor-options", RadioSet).display = event.value
        
    @on(Button.Pressed, "#add-btn")
    def add_hypervisor(self) -> None:
        cfg_mgr: ConfigManager = self.app.config_manager

        name = self.query_one("#name", Input).value.strip()
        address = self.query_one("#address", Input).value.strip()
        port = int(self.query_one("#port", Input).value or "22")
        username = self.query_one("#username", Input).value.strip() or "root"
        auth_method = self.query_one("#auth_method", Select).value
        password = self.query_one("#password", Input).value
        ssh_key_path = self.query_one("#ssh_key_path", Input).value.strip() or None
        is_hypervisor = self.query_one("#hypervisorCheck", Checkbox).value
        selected_button = self.query_one("#hypervisor-options", RadioSet).pressed_button
        hypervisor_type = selected_button.id if selected_button is not None else None

        if is_hypervisor and hypervisor_type is None:
            self.notify("Select a hypervisor type.", severity="error")
            return

        if hypervisor_type == "proxmox-option":
            username = f"{username}@pve"
        
        if not name or not address:
            self.notify("Nickname and hypervisor address are required.", severity="error")
            return

        server = ServerConfig(
            name=name,
            address=address,
            port=port,
            username=username,
            auth_method=auth_method,
            ssh_key_path=ssh_key_path,
            is_hypervisor=is_hypervisor,
        )
        self.query_one("#add-btn", Button).disabled = True
        self.authenticate_host(
            cfg_mgr,
            server,
            password if auth_method == "password" else None,
            username,
            address,
            name,
            is_hypervisor,
        )

    @work(thread=True)
    def authenticate_host(
        self,
        cfg_mgr: ConfigManager,
        server: ServerConfig,
        password: Optional[str],
        username: str,
        address: str,
        name: str,
        is_hypervisor: bool,
    ) -> None:
        try:
            ticket_data = PVEAuthentivation(app=self.app).authenticate(
                username=username,
                password=password,
                host=address,
            )
        except Exception as error:
            self.app.call_from_thread(
                self.authentication_failed,
                error,
            )
            return

        self.app.call_from_thread(
            self.authentication_succeeded,
            cfg_mgr,
            server,
            password,
            name,
            is_hypervisor,
            ticket_data,
        )

    def authentication_failed(self, error: Exception) -> None:
        self.query_one("#add-btn", Button).disabled = False
        cause = getattr(error, "__cause__", None)
        response = getattr(cause, "response", None)
        status_code = getattr(response, "status_code", None)
        if status_code == 401:
            message = "Not authorised: invalid credentials"
        elif status_code == 404:
            message = "Host not found"
        else:
            message = f"Authentication failed: {error}"
        self.notify(message, severity="error")

    def authentication_succeeded(
        self,
        cfg_mgr: ConfigManager,
        server: ServerConfig,
        password: Optional[str],
        name: str,
        is_hypervisor: bool,
        ticket_data: object,
    ) -> None:
        self.query_one("#add-btn", Button).disabled = False
        if not isinstance(ticket_data, dict) or not ticket_data.get("data"):
            self.notify(
                "Authentication failed: unexpected response from host",
                severity="error",
            )
            return

        cfg_mgr.add_server(server, password=password)
        self.notify(f"Added '{name}' ({server.address})")
        for input_id in ("#name", "#address", "#username", "#password", "#ssh_key_path"):
            self.query_one(input_id, Input).value = ""
        self.query_one("#port", Input).value = "22"

        if is_hypervisor:
            self.app.push_screen(AddServerScreen())
        else:
            # configure to add other services through ports
            self.app.push_screen(PollingSettingsScreen())


class AddServerScreen(Screen):
    """Add one server at a time; loops back to itself until user is done."""

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="add-server-box"):
            yield Label("Server nickname")
            yield Input(placeholder="e.g. proxmox-02", id="name")
            yield Label("Server IP address")
            yield Input(placeholder="192.168.1.50", id="address")
            yield Label("Port")
            yield Input(placeholder="22", value="22", id="port")
            yield Label("Username")
            yield Input(placeholder="root", id="username")
            yield Label("Auth method")
            yield Select(
                [("Password", "password"), ("SSH Key", "ssh_key")],
                value="password",
                id="auth_method",
            )
            yield Label("Password (stored securely in your OS keyring, not this file)")
            yield Input(placeholder="", password=True, id="password")
            yield Label("SSH key path (only if using SSH Key auth)")
            yield Input(placeholder="~/.ssh/id_ed25519", id="ssh_key_path")

            with Horizontal():
                yield Button("Add Server", id="add-btn", variant="primary")
                yield Button("Done — Continue", id="done-btn")
        yield Footer()

    @on(Button.Pressed, "#add-btn")
    def add_server(self) -> None:
        cfg_mgr: ConfigManager = self.app.config_manager

        name = self.query_one("#name", Input).value.strip()
        address = self.query_one("#address", Input).value.strip()
        port = int(self.query_one("#port", Input).value or "22")
        username = self.query_one("#username", Input).value.strip() or "root"
        auth_method = self.query_one("#auth_method", Select).value
        password = self.query_one("#password", Input).value
        ssh_key_path = self.query_one("#ssh_key_path", Input).value.strip() or None

        if not name or not address:
            self.notify("Nickname and server address are required.", severity="error")
            return

        server = ServerConfig(
            name=name,
            address=address,
            port=port,
            username=username,
            auth_method=auth_method,
            ssh_key_path=ssh_key_path,
        )
        cfg_mgr.add_server(server, password=password if auth_method == "password" else None)

        self.notify(f"Added '{name}' ({address})")
        # Clear inputs so user can add another
        for input_id in ("#name", "#address", "#username", "#password", "#ssh_key_path"):
            self.query_one(input_id, Input).value = ""
        self.query_one("#port", Input).value = "22"

    @on(Button.Pressed, "#done-btn")
    def finish(self) -> None:
        self.app.push_screen(PollingSettingsScreen())


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
            yield Button("Return", id="back-btn")
        yield Footer()

    @on(Button.Pressed, "#back-btn")
    def finish(self) -> None:
        self.app.push_screen(PollingSettingsScreen())
        
    @on(Button.Pressed, "#finish-btn")
    def finish_setup(self) -> None:
        cfg_mgr: ConfigManager = self.app.config_manager

        print(ConfigManager)
        rate = int(self.query_one("#polling_rate", Input).value or "5")
        theme = self.query_one("#theme", Select).value

        cfg_mgr.config.settings = AppSettings(polling_rate_seconds=rate, theme=theme)
        cfg_mgr.save()

        self.notify("Setup complete!")
        # self.app.pop_screen()  # or push your main Dashboard screen instead
        self.app.push_screen(DashboardScreen())
