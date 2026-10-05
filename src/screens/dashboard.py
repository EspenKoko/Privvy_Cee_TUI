from pathlib import Path
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Header, Footer
from textual.containers import Container, Vertical

from src.widgets.host_Panel import HostPanel
from src.widgets.server_panel import ServerPanel
from src.widgets.dashboard_panel import DashboardPanel

class DashboardScreen(Screen):
    CSS_PATH = str(Path(__file__).resolve().parents[1] / "css" / "dashboard.tcss")

    class RefreshRequested(Message):
        """Request all dashboard panels to reload their data."""

    def on_refresh_requested(self, message: RefreshRequested) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        self.app.config_manager.load()
        self.query_one(DashboardPanel).update_stats()
        self.query_one(HostPanel).refresh_stats()
        self.query_one(ServerPanel).refresh_data()

    def compose(self):
        yield Header(show_clock=True)
        with Vertical():
            yield DashboardPanel(id="dashboard-panel")
            yield HostPanel(id="host-panel")
            with Container(id="server-panel-container"):
                yield ServerPanel(id="server-panel")
        yield Footer()