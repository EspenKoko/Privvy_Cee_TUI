from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Header, Footer, DataTable, Static


class ServerPanel(Vertical):
    CSS = """
    Screen {
        layout: vertical;
    }

    DataTable {
        border: round $secondary;
        height: auto;
    }

    #alerts {
        border: round $error;
        height: auto;
    }
    """
    
    def compose(self)-> ComposeResult:
        yield DataTable(id="vm_table")
        yield DataTable(id="container_table")
        yield Static("Alerts\n• None", id="alerts")
        
    def on_mount(self) -> None:
        vm_table = self.query_one("#vm_table", DataTable)
        vm_table.add_columns("Name", "Status", "CPU", "RAM", "IP", "Uptime")
        vm_table.add_row("Ubuntu Server", "Running", "8%", "3.4GB", "10.0.0.10", "14d")
        vm_table.add_row("Debian Server", "Running", "16%", "2.8GB", "10.0.0.11", "10d")
        vm_table.add_row("Debian Server", "Running", "16%", "2.8GB", "10.0.0.11", "10d")
        vm_table.add_row("Debian Server", "Running", "16%", "2.8GB", "10.0.0.11", "10d")
        vm_table.add_row("Debian Server", "Running", "16%", "2.8GB", "10.0.0.11", "10d")
        vm_table.add_row("Debian Server", "Running", "16%", "2.8GB", "10.0.0.11", "10d")
        vm_table.add_row("Debian Server", "Running", "16%", "2.8GB", "10.0.0.11", "10d")