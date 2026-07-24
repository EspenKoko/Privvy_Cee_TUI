from pathlib import Path

from textual.app import App
from textual.binding import Binding
from src.screens.dashboard import DashboardScreen


class HomelabApp(App):
    """Main application."""

    CSS_PATH = str(Path(__file__).resolve().parent.joinpath("css", "dashboard.tcss"))

    TITLE = "Homelab Dashboard"
    SUB_TITLE = "Proxmox • Docker"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("d", "dashboard", "Dashboard"),
        Binding("r", "refresh", "Refresh"),
        Binding("?", "help", "Help"),
    ]

    def on_mount(self) -> None:
        """Called when the application starts."""
        self.push_screen(DashboardScreen())

    def action_dashboard(self) -> None:
        """Return to the dashboard."""
        self.pop_until_active_screen()

    def action_refresh(self) -> None:
        """Refresh all data."""
        self.post_message(DashboardScreen.RefreshRequested())

    def action_help(self) -> None:
        self.notify("Help coming soon!")