from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import ProgressBar, Label, Static
import psutil
import time

class HostPanel(Vertical):
    CSS = """
    #host-panel {
        border: round $primary;
        height: auto;
        padding: 1;
    }
    
    #metrics {
        height: auto;
    }

    #metrics Horizontal {
        height: 1;
    }

    #extra_stats {
        height: 1fr;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield Label("HOST: Proxmox-01")
        with Vertical(id="metrics"):
            with Horizontal(classes="metric"):
                yield Label("CPU")
                yield ProgressBar(id="cpu_bar", total=100)

            with Horizontal(classes="metric"):
                yield Label("RAM")
                yield ProgressBar(id="ram_bar", total=100)

            with Horizontal(classes="metric"):
                yield Label("Disk")
                yield ProgressBar(id="disk_bar", total=100)
        yield Static(id="net_stats")
        yield Static(id="extra_stats")

    def on_mount(self) -> None:
        self._last_net = psutil.net_io_counters()
        self.set_interval(1.0, self.refresh_stats)

    def refresh_stats(self) -> None:
        self.run_worker(self.poll_metrics, exclusive=True, thread=True)

    def poll_metrics(self) -> None:
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        net = psutil.net_io_counters()
        down_bytes = net.bytes_recv - self._last_net.bytes_recv
        up_bytes = net.bytes_sent - self._last_net.bytes_sent
        self._last_net = net

        down_mb = down_bytes / (1024 * 1024)   # since interval is 1s, this is MB/s
        up_mb = up_bytes / (1024 * 1024)
        
        self.query_one("#cpu_bar", ProgressBar).update(progress=cpu)
        self.query_one("#ram_bar", ProgressBar).update(progress=ram.percent)
        self.query_one("#disk_bar", ProgressBar).update(progress=disk.percent)
        
        def format_speed(bytes_per_sec: float) -> str:
            kb = bytes_per_sec / 1024
            if kb < 1024:
                return f"{kb:.0f}KB/s"
            return f"{kb/1024:.1f}MB/s"

        self.query_one("#net_stats", Static).update(
            f"Network [green]↓ {format_speed(down_bytes)}[/] [orange1]↑ {format_speed(up_bytes)}[/]"
        )

        uptime_seconds = time.time() - psutil.boot_time()
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)

        self.query_one("#extra_stats", Static).update(
            f"Uptime {days}d {hours:02d}h"
        )