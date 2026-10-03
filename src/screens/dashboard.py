from textual.message import Message
from textual.screen import Screen
from textual.widgets import Header, Footer
from textual.containers import VerticalScroll

from src.widgets.host_Panel import HostPanel
from src.widgets.server_panel import ServerPanel
from src.widgets.dashboard_panel import DashboardPanel
from src.widgets.server_panel_v2 import ServersTab

class DashboardScreen(Screen):

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
        with VerticalScroll():
            yield DashboardPanel(id="dashboard-panel")
            yield HostPanel(id="host-panel")
            # yield ServerPanel(id="server-panel")
            yield ServersTab()
            # yield LoginScreen(id="login-panel-2")
        yield Footer()