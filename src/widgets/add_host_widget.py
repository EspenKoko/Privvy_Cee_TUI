from typing import Optional

from textual import on, work
from textual.containers import Center, Vertical, VerticalScroll
from textual.widgets import (
    Button,
    Checkbox,
    Input,
    Label,
    RadioButton,
    RadioSet,
    Select,
)
from textual.app import ComposeResult
from textual.widget import Widget

from src.services.configuration import ConfigManager, ServerConfig
from src.api.pve_access_ticket import PVEAuthentivation


class AddHostWidget(Widget):
    def compose(self) -> ComposeResult:
        with Center(id="add-host-container"):
            with Vertical(id="add-host-content"):
                yield Label("1/3 - Add Host Details", id="add-host-title")
                with VerticalScroll(id="add-host-box"):
                    yield Label("Host Name")
                    yield Input(
                        placeholder="e.g. Dragon warrior",
                        id="name",
                        tooltip="Match casing of the host's name",
                    )
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
                    password_label = Label(
                        "Password (stored securely in your OS keyring)",
                        id="password-label",
                    )
                    password_label.display = True
                    yield password_label
                    password_input = Input(placeholder="login or ssh password for the host", password=True, id="password")
                    password_input.display = True
                    yield password_input
                    ssh_key_label = Label(
                        "SSH key path (only if using SSH Key auth)",
                        id="authmethod-label",
                    )
                    ssh_key_label.display = False
                    yield ssh_key_label
                    ssh_key_input = Input(
                        placeholder="~/.ssh/id_ed25519",
                        id="ssh_key_path",
                    )
                    ssh_key_input.display = False
                    yield ssh_key_input
                    yield Checkbox("Using proxmox", id="hypervisorCheck", value=False)
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

                    yield Button("Add Host", id="add-btn", variant="primary")

    @on(Checkbox.Changed, "#hypervisorCheck")
    def toggle_hypervisor_options(self, event: Checkbox.Changed) -> None:
        self.query_one("#hypervisor-label", Label).display = event.value
        self.query_one("#hypervisor-options", RadioSet).display = event.value

    @on(Select.Changed, "#auth_method")
    def toggle_auth_method_options(self, event: Select.Changed) -> None:
        show_ssh_key_path = event.value == "ssh_key"
        self.query_one("#authmethod-label", Label).display = show_ssh_key_path
        self.query_one("#ssh_key_path", Input).display = show_ssh_key_path
        self.query_one("#password-label", Label).display = not show_ssh_key_path
        self.query_one("#password", Input).display = not show_ssh_key_path

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
            self.app.call_from_thread(self.authentication_failed, error)
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

        from src.screens.setup_wizard import AddServerScreen, PollingSettingsScreen

        next_screen = AddServerScreen if is_hypervisor else PollingSettingsScreen
        self.app.push_screen(next_screen())