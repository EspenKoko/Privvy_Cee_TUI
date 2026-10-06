from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.timer import Timer
from textual.widgets import Label, Static

from src.api.pve_api_service import CallProxmox
from src.models.node_details_type import (
    NodeNetworkInterface,
    NodeNetworkResponse,
    NodeStatusData,
    NodeStatusResponse,
)
from src.services.api_call_paths import ProxmoxApiPaths
from src.services.polling_rate import PollingRateService

class HostPanelDetails(Vertical):
    _css_path = Path(__file__).resolve().parents[1] / "css" / "host_panel.tcss"
    DEFAULT_CSS = _css_path.read_text(encoding="utf-8")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._polling_enabled = True
        self._polling_timer: Timer | None = None
    
    def compose(self) -> ComposeResult:
        # yield Label("HOST: <hostname>", id="host-details-label", classes="host-label")
        with Vertical(id="host-details-metrics"):
            with Horizontal(classes="metric"):
                yield Label("CPU", classes="labels")
                yield Static("Loading...", id="cpu-details", markup=False)

            with Horizontal(classes="metric"):
                yield Label("RAM", classes="labels")
                yield Static("Loading...", id="ram-details", markup=False)

            with Horizontal(classes="metric"):
                yield Label("Disk", classes="labels")
                yield Static("Loading...", id="disk-details", markup=False)

            with Horizontal(classes="metric"):
                yield Label("IPv4", classes="labels")
                yield Static("Loading...", id="ipv4-details", markup=False)

            with Horizontal(classes="metric"):
                yield Label("Bridge", classes="labels")
                yield Static("Loading...", id="bridge-details", markup=False)

            # with Horizontal(classes="metric"):
            #     yield Label("Uptime", classes="labels")
            #     yield Static("Loading...", id="uptime-details", markup=False)

    def on_mount(self) -> None:
        self._polling_enabled = True
        config_manager = getattr(self.app, "config_manager", None)
        interval = PollingRateService.get_polling_rate_seconds(config_manager)
        self.refresh_details()
        self._polling_timer = self.set_interval(interval, self.refresh_details)

    def stop_polling(self) -> None:
        self._polling_enabled = False
        if self._polling_timer is not None:
            self._polling_timer.stop()
            self._polling_timer = None

    def refresh_details(self) -> None:
        if not self._polling_enabled:
            return
        self.run_worker(self.poll_details, exclusive=True, thread=True)

    def poll_details(self) -> None:
        if not self._polling_enabled:
            return
        config_manager = getattr(self.app, "config_manager", None)
        if config_manager is None:
            self.app.call_from_thread(
                self._show_error, "No configuration manager is available."
            )
            return

        try:
            hosts = config_manager.load().hosts
            if not self._polling_enabled:
                return
            if not hosts:
                self.app.call_from_thread(
                    self._show_error, "No Proxmox hosts are configured."
                )
                return

            api = CallProxmox(app=self.app)
            last_error = None
            for host in hosts:
                if not self._polling_enabled:
                    return
                try:
                    status_response = api.call_proxmox(
                        ProxmoxApiPaths.node_status(host.name), host=host.address
                    )
                    if not self._polling_enabled:
                        return
                    network_response = api.call_proxmox(
                        ProxmoxApiPaths.node_network(host.name), host=host.address
                    )
                    status = NodeStatusResponse.model_validate(status_response).data
                    network = NodeNetworkResponse.model_validate(network_response)
                except (RuntimeError, ValueError) as error:
                    last_error = str(error)
                    continue

                self.app.call_from_thread(
                    self._update_details, status, network.data, host.name
                )
                return

            message = last_error or "Could not load details for a configured node."
            self.app.call_from_thread(self._show_error, message)
        except (OSError, ValueError, RuntimeError) as error:
            if self._polling_enabled:
                self.app.call_from_thread(self._show_error, str(error))

    def _update_details(
        self,
        status: NodeStatusData,
        interfaces: list[NodeNetworkInterface],
        configured_name: str,
    ) -> None:
        if not self._polling_enabled:
            return

        cpu = status.cpuinfo
        cpu_model = cpu.model if cpu and cpu.model else "Unknown CPU"
        cores = cpu.cores if cpu and cpu.cores is not None else "?"
        sockets = cpu.sockets if cpu and cpu.sockets is not None else "?"
        threads = cpu.cpus if cpu and cpu.cpus is not None else "?"

        memory = status.memory
        rootfs = status.rootfs
        memory_percent = self._usage_percent(memory.used, memory.total)
        disk_percent = self._usage_percent(rootfs.used, rootfs.total)

        bridges = [
            interface
            for interface in interfaces
            if interface.type == "bridge" or interface.bridge_ports is not None
        ]
        bridge = next(
            (interface for interface in bridges if interface.address or interface.cidr),
            bridges[0] if bridges else None,
        )
        ipv4 = self._format_ipv4(bridge) if bridge else "Not reported"
        bridge_name = bridge.iface if bridge else "Not reported"
        if bridge and bridge.bridge_ports:
            bridge_name = f"{bridge_name} (ports: {bridge.bridge_ports})"

        uptime_days, remainder = divmod(status.uptime, 86400)
        uptime_hours = remainder // 3600
        # self.query_one("#host-details-label", Label).update(f"HOST: {configured_name}")
        self.query_one("#cpu-details", Static).update(
            f"{cpu_model} ({cores} cores, {threads} threads, {sockets} socket(s))"
        )
        self.query_one("#ram-details", Static).update(
            f"{self._format_bytes(memory.used)} used / "
            f"{self._format_bytes(memory.total)} total ({memory_percent:.1f}%)"
        )
        self.query_one("#disk-details", Static).update(
            f"{self._format_bytes(rootfs.used)} used / "
            f"{self._format_bytes(rootfs.total)} total ({disk_percent:.1f}%)"
        )
        self.query_one("#ipv4-details", Static).update(ipv4)
        self.query_one("#bridge-details", Static).update(bridge_name)
        # self.query_one("#uptime-details", Static).update(
        #     f"{uptime_days}d {uptime_hours:02d}h"
        # )

    @staticmethod
    def _format_ipv4(interface: NodeNetworkInterface) -> str:
        if interface.cidr:
            return interface.cidr
        if interface.address and interface.netmask:
            return f"{interface.address}/{interface.netmask}"
        return interface.address or "Not reported"

    @staticmethod
    def _format_bytes(value: int) -> str:
        return f"{value / (1024 ** 3):.1f} GiB"

    @staticmethod
    def _usage_percent(used: int, total: int) -> float:
        if total <= 0:
            return 0.0
        return max(0.0, min(100.0, used / total * 100))

    def _show_error(self, message: str) -> None:
        if not self._polling_enabled:
            return
        # self.query_one("#host-details-label", Label).update("HOST: unavailable")
        for detail_id in (
            "#cpu-details",
            "#ram-details",
            "#disk-details",
            "#ipv4-details",
            "#bridge-details",
        ):
            self.query_one(detail_id, Static).update(message)
        