from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll, Widget

from src.widgets.host_Panel_details import HostPanelDetails
from src.widgets.dashboard_headers import DashboardHeaders
from src.widgets.host_Panel import HostPanel
from src.widgets.server_panel import ServerPanel


class DashboardPanel(Widget):
    
    def compose(self) -> ComposeResult:
        with VerticalScroll(id="dashboard-content"):
            with Horizontal(id="host-summary-row"):
                yield HostPanel(id="host-panel")
                yield HostPanelDetails(id="host-panel-details")
            with Container(id="server-panel-container"):
                yield ServerPanel(id="server-panel")