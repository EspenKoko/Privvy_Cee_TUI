from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.timer import Timer
from textual.widgets import ProgressBar, Label, Static

from src.api.pve_api_service import CallProxmox
from src.services.api_call_paths import ProxmoxApiPaths

class HostPanel(Vertical):
    _css_path = Path(__file__).resolve().parents[1] / "css" / "host_panel.tcss"
    DEFAULT_CSS = _css_path.read_text(encoding="utf-8")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._polling_enabled = True
        self._polling_timer: Timer | None = None
    
    def compose(self) -> ComposeResult:
        yield Label("HOST: <hostname>", id="host-label", classes="host-label")
        with Vertical(id="metrics"):
            with Horizontal(classes="metric"):
                yield Label("CPU", classes="labels")
                yield ProgressBar(id="cpu_bar", total=100, classes="progress-bar")

            with Horizontal(classes="metric"):
                yield Label("RAM", classes="labels")
                yield ProgressBar(id="ram_bar", total=100, classes="progress-bar")

            with Horizontal(classes="metric"):
                yield Label("Disk", classes="labels")
                yield ProgressBar(id="disk_bar", total=100, classes="progress-bar")
                
            with Horizontal(classes="metric"):
                yield Label("Uptime", classes="labels")
                yield Static(id="extra_stats")

    def on_mount(self) -> None:
        self.refresh_stats()
        self._polling_timer = self.set_interval(1.0, self.refresh_stats)

    def stop_polling(self) -> None:
        self._polling_enabled = False
        if self._polling_timer is not None:
            self._polling_timer.stop()
            self._polling_timer = None

    def refresh_stats(self) -> None:
        if not self._polling_enabled:
            return
        self.run_worker(self.poll_metrics, exclusive=True, thread=True)

    def poll_metrics(self) -> None:
        if not self._polling_enabled:
            return
        config_manager = getattr(self.app, "config_manager", None)
        if config_manager is None:
            self.app.call_from_thread(
                self._show_api_error, "No configuration manager is available."
            )
            return

        try:
            hosts = config_manager.load().hosts
            if not self._polling_enabled:
                return
            if not hosts:
                self.app.call_from_thread(
                    self._show_api_error, "No Proxmox hosts are configured."
                )
                return

            api = CallProxmox(app=self.app)
            last_error = None
            for host in hosts:
                if not self._polling_enabled:
                    return
                try:
                    response = api.call_proxmox(
                        ProxmoxApiPaths.nodes(), host=host.address
                    )
                except RuntimeError as error:
                    last_error = str(error)
                    continue

                nodes = response.get("data", []) if isinstance(response, dict) else []
                node = next(
                    (
                        item
                        for item in nodes
                        if isinstance(item, dict)
                        and (
                            item.get("node") == host.name
                            or item.get("id") == f"node/{host.name}"
                        )
                    ),
                    None,
                )
                if node is not None:
                    self.app.call_from_thread(self._update_metrics, node, host.name)
                    return

            message = last_error or "No API node matched a configured host."
            self.app.call_from_thread(self._show_api_error, message)
        except (OSError, ValueError, RuntimeError) as error:
            if self._polling_enabled:
                self.app.call_from_thread(self._show_api_error, str(error))

    def _update_metrics(self, node: dict, configured_name: str) -> None:
        if not self._polling_enabled:
            return

        def percentage(value_name: str, maximum_name: str) -> float:
            maximum = float(node.get(maximum_name) or 0)
            if maximum <= 0:
                return 0
            value = float(node.get(value_name) or 0)
            return max(0, min(100, value / maximum * 100))

        cpu_percent = max(0, min(100, float(node.get("cpu") or 0) * 100))
        self.query_one("#host-label", Label).update(f"HOST: {configured_name}")
        self.query_one("#cpu_bar", ProgressBar).update(progress=cpu_percent)
        self.query_one("#ram_bar", ProgressBar).update(
            progress=percentage("mem", "maxmem")
        )
        self.query_one("#disk_bar", ProgressBar).update(
            progress=percentage("disk", "maxdisk")
        )
        # self.query_one("#net_stats", Static).update(
        #     "Unavailable from the /nodes endpoint"
        # )

        uptime_seconds = int(node.get("uptime") or 0)
        days, remainder = divmod(uptime_seconds, 86400)
        hours = remainder // 3600
        self.query_one("#extra_stats", Static).update(f"{days}d {hours:02d}h")

    def _show_api_error(self, message: str) -> None:
        if not self._polling_enabled:
            return
        self.query_one("#host-label", Label).update("HOST: API unavailable")
        self.query_one("#extra_stats", Static).update(f"[red]{message}[/red]")
        