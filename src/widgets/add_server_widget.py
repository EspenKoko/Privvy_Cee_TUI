from textual import on
from textual.app import ComposeResult
from textual.containers import Center, Vertical, VerticalScroll
from textual.widget import Widget
from textual.widgets import Button, Input, Label, Select

from src.services.configuration import ConfigManager, ServerConfig


class AddServerWidget(Widget):
    def compose(self) -> ComposeResult:
        with Center(id="add-server-container"):
            with Vertical(id="add-server-content"):
                yield Label("2/3 - Add Server Details", id="add-server-title")
                with VerticalScroll(id="add-server-box"):
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
                    yield Label("Password (stored securely in your OS keyring)")
                    yield Input(placeholder="", password=True, id="password")
                    yield Label("SSH key path (only if using SSH Key auth)")
                    yield Input(placeholder="~/.ssh/id_ed25519", id="ssh_key_path")

                    yield Button("Add Server", id="add-btn", variant="primary")
                    yield Button("Done — Continue", id="done-btn")

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
        for input_id in ("#name", "#address", "#username", "#password", "#ssh_key_path"):
            self.query_one(input_id, Input).value = ""
        self.query_one("#port", Input).value = "22"

    @on(Button.Pressed, "#done-btn")
    def finish(self) -> None:
        from src.screens.setup_wizard import PollingSettingsScreen

        self.app.push_screen(PollingSettingsScreen())