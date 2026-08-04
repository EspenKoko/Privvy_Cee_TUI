from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Static, DataTable, Input, Label, Button, Select
from textual.app import ComposeResult
from textual import on

from src.services.configuration import ConfigManager, ServerConfig, AppSettings

class ServerConfiguration(Horizontal):
    
    DEFAULT_CSS = """
    #settings-body {
        layout: horizontal;
        height: 1fr;
    }

    #server-list-pane {
        width: 45%;
        border: solid $primary;
        padding: 1;
    }

    #server-edit-pane {
        width: 55%;
        border: solid $secondary;
        padding: 1;
    }

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
        
    def compose(self) -> ComposeResult:
        with Horizontal(id="settings-body"):
            with VerticalScroll(id="server-list-pane"):
                yield Static("[b]Configured Servers[/b]")
                yield DataTable(id="server-table", cursor_type="row", zebra_stripes=True)
                with Horizontal(classes="button-row"):
                    yield Button("Add New", id="add-new-btn", variant="primary")
                    yield Button("Delete Selected", id="delete-btn", variant="error")

            with VerticalScroll(id="server-edit-pane"):
                yield Static("[b]New Server[/b]", id="edit-pane-title")
                yield Label("Nickname", classes="field-label")
                yield Input(placeholder="e.g. proxmox-01", id="edit-name")
                yield Label("Host / IP address", classes="field-label")
                yield Input(placeholder="192.168.1.50", id="edit-host")
                yield Label("Port", classes="field-label")
                yield Input(placeholder="22", id="edit-port")
                yield Label("Username", classes="field-label")
                yield Input(placeholder="root", id="edit-username")
                yield Label("Auth method", classes="field-label")
                yield Select(
                    [("Password", "password"), ("SSH Key", "ssh_key")],
                    value="password",
                    id="edit-auth-method",
                )
                yield Label(
                    "Password (leave blank to keep existing)",
                    classes="field-label",
                    id="edit-password-label",
                )
                yield Input(password=True, id="edit-password")
                yield Label("SSH key path", classes="field-label", id="edit-ssh-key-label")
                yield Input(placeholder="~/.ssh/id_ed25519", id="edit-ssh-key-path")

                with Horizontal(classes="button-row"):
                    yield Button("Save Server", id="save-server-btn", variant="success")
                    yield Button("Cancel", id="cancel-edit-btn")
            yield Static("", id="status-line")

    def on_mount(self) -> None:
        table = self.query_one("#server-table", DataTable)
        table.add_columns("Name", "Host", "Port", "Username", "Auth")
        self._refresh_table()
        self._clear_edit_form()

    def _refresh_table(self) -> None:
        table = self.query_one("#server-table", DataTable)
        table.clear()
        cfg_mgr: ConfigManager = self.app.config_manager
        for server in cfg_mgr.config.servers:
            table.add_row(
                server.name, server.host, str(server.port),
                server.username, server.auth_method, key=server.name,
            )

    # ---------- Table selection -> populate edit form ----------

    @on(DataTable.RowSelected, "#server-table")
    # def on_row_selected(self, event: DataTable.RowSelected) -> None:
    def on_row_selected(self, event: DataTable.RowHighlighted) -> None:
        if event.row_key is None:
            return
        
        server_name = event.row_key.value
        cfg_mgr: ConfigManager = self.app.config_manager
        server = next((s for s in cfg_mgr.config.servers if s.name == server_name), None)

        if not server:
            return

        self.editing_server_name = server.name
        self.query_one("#edit-pane-title", Static).update(f"[b]Editing: {server.name}[/b]")
        self.query_one("#edit-name", Input).value = server.name
        self.query_one("#edit-host", Input).value = server.host
        self.query_one("#edit-port", Input).value = str(server.port)
        self.query_one("#edit-username", Input).value = server.username
        self.query_one("#edit-auth-method", Select).value = server.auth_method
        self.query_one("#edit-password", Input).value = ""  # never re-display stored secret
        self.query_one("#edit-ssh-key-path", Input).value = server.ssh_key_path or ""
        self._toggle_auth_fields(server.auth_method)
        self._set_status("")

    # ---------- Auth method toggling ----------

    @on(Select.Changed, "#edit-auth-method")
    def on_auth_method_changed(self, event: Select.Changed) -> None:
        self._toggle_auth_fields(event.value)

    def _toggle_auth_fields(self, auth_method: str) -> None:
        is_key_auth = auth_method == "ssh_key"
        self.query_one("#edit-password-label", Label).display = not is_key_auth
        self.query_one("#edit-password", Input).display = not is_key_auth
        self.query_one("#edit-ssh-key-label", Label).display = is_key_auth
        self.query_one("#edit-ssh-key-path", Input).display = is_key_auth

    # ---------- Add / Cancel ----------

    @on(Button.Pressed, "#add-new-btn")
    def on_add_new(self) -> None:
        self._clear_edit_form()

    @on(Button.Pressed, "#cancel-edit-btn")
    def on_cancel_edit(self) -> None:
        self._clear_edit_form()

    def _clear_edit_form(self) -> None:
        self.editing_server_name = None
        self.query_one("#edit-pane-title", Static).update("[b]New Server[/b]")
        self.query_one("#edit-name", Input).value = ""
        self.query_one("#edit-host", Input).value = ""
        self.query_one("#edit-port", Input).value = "22"
        self.query_one("#edit-username", Input).value = "root"
        self.query_one("#edit-auth-method", Select).value = "password"
        self.query_one("#edit-password", Input).value = ""
        self.query_one("#edit-ssh-key-path", Input).value = ""
        self._toggle_auth_fields("password")
        self._set_status("")

    # ---------- Save server (create or update) ----------

    @on(Button.Pressed, "#save-server-btn")
    def on_save_server(self) -> None:
        cfg_mgr: ConfigManager = self.app.config_manager

        name = self.query_one("#edit-name", Input).value.strip()
        host = self.query_one("#edit-host", Input).value.strip()
        port_raw = self.query_one("#edit-port", Input).value.strip()
        username = self.query_one("#edit-username", Input).value.strip() or "root"
        auth_method = self.query_one("#edit-auth-method", Select).value
        password = self.query_one("#edit-password", Input).value
        ssh_key_path = self.query_one("#edit-ssh-key-path", Input).value.strip() or None

        if not name or not host:
            self._set_status("[red]Nickname and host are required.[/red]")
            return
        try:
            port = int(port_raw) if port_raw else 22
        except ValueError:
            self._set_status("[red]Port must be a number.[/red]")
            return

        existing_names = {s.name for s in cfg_mgr.config.servers}

        if self.editing_server_name is None:
            # ---- Adding a brand new server ----
            if name in existing_names:
                self._set_status(f"[red]A server named '{name}' already exists.[/red]")
                return
            new_server = ServerConfig(
                name=name, host=host, port=port, username=username,
                auth_method=auth_method, ssh_key_path=ssh_key_path,
            )
            cfg_mgr.add_server(new_server, password=password if auth_method == "password" else None)
            self._set_status(f"[green]Added '{name}'.[/green]")

        else:
            # ---- Updating an existing server ----
            old_name = self.editing_server_name
            old_server = next(s for s in cfg_mgr.config.servers if s.name == old_name)

            if name != old_name and name in existing_names:
                self._set_status(f"[red]A server named '{name}' already exists.[/red]")
                return

            # If the name or username changes, the keyring lookup key changes too —
            # move the stored secret across rather than silently orphaning it.
            key_changed = (name != old_server.name) or (username != old_server.username)
            existing_password = cfg_mgr.get_password(old_server) if auth_method == "password" else None

            if key_changed:
                cfg_mgr.delete_password(old_server)

            old_server.name = name
            old_server.host = host
            old_server.port = port
            old_server.username = username
            old_server.auth_method = auth_method
            old_server.ssh_key_path = ssh_key_path

            if auth_method == "password":
                new_password = password or existing_password
                if new_password:
                    cfg_mgr.set_password(old_server, new_password)

            cfg_mgr.save()
            self.editing_server_name = name
            self._set_status(f"[green]Saved changes to '{name}'.[/green]")

        self._refresh_table()

    # ---------- Delete server ----------

    @on(Button.Pressed, "#delete-btn")
    def on_delete(self) -> None:
        table = self.query_one("#server-table", DataTable)
        if table.cursor_row is None:
            self._set_status("[red]Select a server in the table first.[/red]")
            return

        row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
        server_name = row_key.value
        cfg_mgr: ConfigManager = self.app.config_manager
        cfg_mgr.remove_server(server_name)

        self._refresh_table()
        self._clear_edit_form()
        self._set_status(f"[yellow]Deleted '{server_name}'.[/yellow]")

    # ---------- Helpers ----------

    def _set_status(self, message: str) -> None:
        self.query_one("#status-line", Static).update(message)