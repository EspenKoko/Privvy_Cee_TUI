from textual.screen import Screen
from textual.widgets import Header, Footer
from textual.containers import VerticalScroll

from src.widgets.host_Panel import HostPanel
from src.widgets.server_panel import ServerPanel
from src.widgets.dashboard_panel import DashboardPanel


class DashboardScreen(Screen):

    def compose(self):
        yield Header(show_clock=True)
        with VerticalScroll():
            yield DashboardPanel()
            yield HostPanel(id="host-panel")
            # yield HostPanel(id="host-panel-2")
            yield ServerPanel(id="server-panel")
        yield Footer()