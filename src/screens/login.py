"""
A Textual (https://textual.textualize.io) terminal UI with two screens:

1. A login/sign-up screen with a tabbed header ("Log In" / "Sign Up"),
   whose active form is centered on the screen.
2. A dashboard screen (routed to after a successful login) that also has
   a tabbed header ("Servers" / "Activity Log"). The "Servers" tab shows
   a table of dummy server metrics, and every row has Start / Shut Down /
   Restart buttons that update that server's status live.

Install & run:
    pip install textual
    python login_app.py

Quit with "q" or Ctrl+C. On the dashboard, "l" logs out back to the login
screen.
"""

from __future__ import annotations

from dataclasses import dataclass

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Header,
    Footer,
    TabbedContent,
    TabPane,
    Input,
    Button,
    Label,
    Static,
)


# --------------------------------------------------------------------------
# Dummy data
# --------------------------------------------------------------------------

@dataclass
class ServerInfo:
    name: str
    status: str  # "Running" | "Stopped" | "Restarting"
    cpu: int
    mem: int
    uptime: str


DUMMY_SERVERS = [
    ServerInfo("web-01", "Running", 34, 62, "5d 3h"),
    ServerInfo("web-02", "Running", 28, 55, "5d 3h"),
    ServerInfo("db-primary", "Running", 71, 88, "12d 7h"),
    ServerInfo("db-replica", "Stopped", 0, 4, "-"),
    ServerInfo("cache-01", "Running", 12, 30, "2d 14h"),
    ServerInfo("worker-01", "Stopped", 0, 2, "-"),
    ServerInfo("web-01", "Running", 34, 62, "5d 3h"),
    ServerInfo("web-02", "Running", 28, 55, "5d 3h"),
    ServerInfo("db-primary", "Running", 71, 88, "12d 7h"),
    ServerInfo("db-replica", "Stopped", 0, 4, "-"),
    ServerInfo("cache-01", "Running", 12, 30, "2d 14h"),
    ServerInfo("worker-01", "Stopped", 0, 2, "-"),
]

ACTIVITY_LOG = [
    "web-01 restarted successfully",
    "db-replica shut down for maintenance",
    "cache-01 CPU spike resolved",
    "worker-01 stopped by admin",
    "web-02 deployed new build",
]

STATUS_COLOR = {
    "Running": "green",
    "Stopped": "red",
    "Restarting": "yellow",
}


def slugify(name: str) -> str:
    return name.replace(".", "-").replace(" ", "-").lower()


# --------------------------------------------------------------------------
# Login screen
# --------------------------------------------------------------------------

class LoginForm(Vertical):
    """The centered log-in form."""

    def compose(self) -> ComposeResult:
        yield Label("Welcome back", id="login-title")
        yield Label("Sign in to continue", id="login-subtitle")
        yield Input(placeholder="Username", id="username")
        yield Input(placeholder="Password", password=True, id="password")
        yield Button("Log In", variant="primary", id="login-button")
        yield Label("", id="login-status")


class SignUpForm(Vertical):
    """The centered sign-up form."""

    def compose(self) -> ComposeResult:
        yield Label("Create an account", id="signup-title")
        yield Label("It only takes a minute", id="signup-subtitle")
        yield Input(placeholder="Full name", id="fullname")
        yield Input(placeholder="Email", id="email")
        yield Input(placeholder="Password", password=True, id="signup-password")
        yield Button("Sign Up", variant="success", id="signup-button")
        yield Label("", id="signup-status")


class LoginScreen(Screen):
    """Tabbed login/sign-up screen; the active form is centered."""

    CSS = """
    LoginScreen {
        align: center middle;
    }

    #card {
        width: 64;
        height: auto;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    TabbedContent {
        width: 100%;
        height: auto;
    }

    TabPane {
        align: center middle;
        height: auto;
        padding: 1 0;
    }

    LoginForm, SignUpForm {
        width: 100%;
        height: auto;
        align: center middle;
    }

    #login-title, #signup-title {
        text-style: bold;
        content-align: center middle;
        width: 100%;
    }

    #login-subtitle, #signup-subtitle {
        color: $text-muted;
        content-align: center middle;
        width: 100%;
        margin-bottom: 1;
    }

    LoginForm Input, SignUpForm Input {
        width: 42;
        margin: 1 0;
    }

    LoginForm Button, SignUpForm Button {
        width: 42;
        margin-top: 1;
    }

    #login-status, #signup-status {
        content-align: center middle;
        width: 100%;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="card"):
            with TabbedContent(initial="login-tab"):
                with TabPane("Log In", id="login-tab"):
                    yield LoginForm()
                with TabPane("Sign Up", id="signup-tab"):
                    yield SignUpForm()
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "login-button":
            username = self.query_one("#username", Input).value.strip()
            password = self.query_one("#password", Input).value
            status = self.query_one("#login-status", Label)
            if username and password:
                status.update("")
                self.app.push_screen(DashboardScreen(username))
            else:
                status.update("Please enter both username and password.")
                status.styles.color = "red"
        elif event.button.id == "signup-button":
            fullname = self.query_one("#fullname", Input).value.strip()
            email = self.query_one("#email", Input).value.strip()
            status = self.query_one("#signup-status", Label)
            if fullname and email:
                status.update("Account created — you can now log in.")
                status.styles.color = "green"
            else:
                status.update("Please fill in all fields.")
                status.styles.color = "red"


# --------------------------------------------------------------------------
# Dashboard screen (routed to after login)
# --------------------------------------------------------------------------

class ServerRow(Horizontal):
    """One row of the server table: metrics + start/shutdown/restart buttons."""

    def __init__(self, server: ServerInfo) -> None:
        super().__init__(classes="row data-row")
        self.server = server
        self.slug = slugify(server.name)

    def compose(self) -> ComposeResult:
        yield Label(self.server.name, classes="col-server")
        status_label = Label(self.server.status, id=f"status-{self.slug}", classes="col-status")
        status_label.styles.color = STATUS_COLOR[self.server.status]
        yield status_label
        yield Label(f"{self.server.cpu}%", id=f"cpu-{self.slug}", classes="col-cpu")
        yield Label(f"{self.server.mem}%", id=f"mem-{self.slug}", classes="col-mem")
        yield Label(self.server.uptime, id=f"uptime-{self.slug}", classes="col-uptime")
        with Horizontal(classes="col-actions"):
            yield Button("Start", id=f"start-{self.slug}", variant="success", classes="row-btn")
            yield Button("Shut Down", id=f"shutdown-{self.slug}", variant="error", classes="row-btn")
            yield Button("Restart", id=f"restart-{self.slug}", variant="warning", classes="row-btn")


class ServersTab(VerticalScroll):
    """The 'Servers' tab: a header row plus a ServerRow per server."""

    def compose(self) -> ComposeResult:
        with Horizontal(classes="row header-row"):
            yield Label("Server", classes="col-server")
            yield Label("Status", classes="col-status")
            yield Label("CPU", classes="col-cpu")
            yield Label("Mem", classes="col-mem")
            yield Label("Uptime", classes="col-uptime")
            yield Label("Actions", classes="col-actions")
        for server in DUMMY_SERVERS:
            yield ServerRow(server)

    def set_status(self, slug: str, status: str) -> None:
        label = self.query_one(f"#status-{slug}", Label)
        label.update(status)
        label.styles.color = STATUS_COLOR[status]


class ActivityLogTab(VerticalScroll):
    """The 'Activity Log' tab: a simple list of recent dummy events."""

    def compose(self) -> ComposeResult:
        for entry in ACTIVITY_LOG:
            yield Static(f"• {entry}", classes="log-entry")


class DashboardScreen(Screen):
    """Tabbed dashboard shown after a successful login."""

    BINDINGS = [("l", "logout", "Log out")]

    CSS = """
    #dashboard-card {
        width: 90%;
        height: 1fr;
        margin: 1 2;
        border: round $accent;
        padding: 1 2;
    }

    #welcome {
        text-style: bold;
        margin-bottom: 1;
    }

    .row {
        height: 3;
    }

    .header-row {
        text-style: bold;
        border-bottom: solid $accent;
    }

    .col-server { width: 16; content-align: left middle; }
    .col-status { width: 13; content-align: left middle; }
    .col-cpu { width: 7; content-align: left middle; }
    .col-mem { width: 7; content-align: left middle; }
    .col-uptime { width: 12; content-align: left middle; }
    .col-actions { width: 1fr; content-align: left middle; }

    .row-btn {
        min-width: 11;
        width: auto;
        height: 3;
        margin-right: 1;
    }

    .log-entry {
        padding: 0 1;
        height: auto;
    }
    """

    def __init__(self, username: str) -> None:
        super().__init__()
        self.username = username

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="dashboard-card"):
            yield Label(f"Welcome, {self.username} — Server Dashboard", id="welcome")
            with TabbedContent(initial="servers-tab"):
                with TabPane("Servers", id="servers-tab"):
                    yield ServersTab()
                with TabPane("Activity Log", id="log-tab"):
                    yield ActivityLogTab()
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""
        if "-" not in button_id:
            return
        action, slug = button_id.split("-", 1)
        servers_tab = self.query_one(ServersTab)

        if action == "start":
            servers_tab.set_status(slug, "Running")
            self.notify(f"{slug} started")
        elif action == "shutdown":
            servers_tab.set_status(slug, "Stopped")
            self.notify(f"{slug} shut down", severity="warning")
        elif action == "restart":
            servers_tab.set_status(slug, "Restarting")
            self.notify(f"{slug} restarting…")
            self.set_timer(1.5, lambda: servers_tab.set_status(slug, "Running"))

    def action_logout(self) -> None:
        self.app.pop_screen()


# --------------------------------------------------------------------------
# App
# --------------------------------------------------------------------------

class LoginApp(App):
    """Login screen routes to a tabbed server dashboard on success."""

    TITLE = "Account Access"
    BINDINGS = [("q", "quit", "Quit")]

    def on_mount(self) -> None:
        self.push_screen(LoginScreen())


if __name__ == "__main__":
    LoginApp().run()