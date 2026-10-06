
from dataclasses import dataclass
from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.timer import Timer
from textual.widgets import (
    Button,
    Label,
)
from src.api.pve_api_service import CallProxmox
from src.services.api_call_paths import ProxmoxApiPaths
from src.models.lxc_type import ProxmoxCT
from src.models.qemu_type import ProxmoxVM
from src.services.polling_rate import PollingRateService

@dataclass
class ServerInfo:
    id: int
    name: str
    type: str
    status: str  # "Running" | "Stopped" | "Restarting"
    cpu: float
    mem: int
    total_ram: str
    uptime: str
    node: str | None = None

STATUS_COLOR = {
    "Running": "green",
    "Stopped": "red",
    "Restarting": "yellow",
}

def slugify(name: str, id: int) -> str:
    server = name.replace(".", "").replace("-", "").replace(" ", "").lower()
    return f"{server}-{id}"

class ServerRow(Horizontal):
    """One row of the server table: metrics + start/shutdown/restart buttons."""

    def __init__(self, server: ServerInfo) -> None:
        super().__init__(classes="row data-row")
        self.server = server
        self.slug = slugify(server.name, server.id)

    def compose(self) -> ComposeResult:
        yield Label(self.server.name, classes="col-server")
        yield Label(self.server.type, classes="col-type")
        status_label = Label(self.server.status, id=f"status-{self.slug}", classes="col-status")
        status_label.styles.color = STATUS_COLOR[self.server.status]
        yield status_label
        yield Label(f"{self.server.cpu:.1f}%", id=f"cpu-{self.slug}", classes="col-cpu")
        yield Label(f"{self.server.mem}%", id=f"mem-{self.slug}", classes="col-memusage")
        yield Label(self.server.total_ram, id=f"total-ram-{self.slug}", classes="col-memtotal")
        yield Label(self.server.uptime, id=f"uptime-{self.slug}", classes="col-uptime")
        with Horizontal(classes="col-actions"):
            yield Button("Start", id=f"start-{self.slug}", variant="success", classes="row-btn")
            yield Button("Shut Down", id=f"shutdown-{self.slug}", variant="error", classes="row-btn")
            yield Button("Restart", id=f"restart-{self.slug}", variant="warning", classes="row-btn")
    
    def update_server(self, server: ServerInfo) -> None:
        self.server = server
        status = self.query_one(f"#status-{self.slug}", Label)
        status.update(server.status)
        status.styles.color = STATUS_COLOR[server.status]
        self.query_one(f"#cpu-{self.slug}", Label).update(f"{server.cpu:.1f}%")
        self.query_one(f"#mem-{self.slug}", Label).update(f"{server.mem}%")
        self.query_one(f"#total-ram-{self.slug}", Label).update(server.total_ram)
        self.query_one(f"#uptime-{self.slug}", Label).update(server.uptime)

class ServerPanel(VerticalScroll):
    """The 'Servers' tab: a header row plus a ServerRow per server."""

    _css_path = Path(__file__).resolve().parents[1] / "css" / "server_panel.tcss"
    DEFAULT_CSS = _css_path.read_text(encoding="utf-8")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.servers: list[ServerInfo] = []
        self._fetching = False
        self._polling_enabled = True
        self._polling_timer: Timer | None = None
        
    def compose(self) -> ComposeResult:
        with Horizontal(classes="row header-row"):
            yield Label("Server", classes="col-server")
            yield Label("Type", classes="col-type")
            yield Label("Status", classes="col-status")
            yield Label("CPU", classes="col-cpu")
            yield Label("Mem Usage", classes="col-memusage")
            yield Label("Total RAM", classes="col-memtotal")
            yield Label("Uptime", classes="col-uptime")
            # yield Label("Ip", classes="col-ip")
            yield Label("Actions", classes="col-actions")
        for server in self.servers:
            yield ServerRow(server)

    def on_mount(self) -> None:
        self.refresh_data()
        self.update_polling_interval()

    def update_polling_interval(self) -> None:
        if not self._polling_enabled:
            return
        if self._polling_timer is not None:
            self._polling_timer.stop()
        polling_rate = PollingRateService.get_polling_rate_seconds(
            self.app.config_manager
        )
        self._polling_timer = self.set_interval(polling_rate, self.refresh_data)

    def stop_polling(self) -> None:
        self._polling_enabled = False
        if self._polling_timer is not None:
            self._polling_timer.stop()
            self._polling_timer = None

    def refresh_data(self) -> None:
        if not self._polling_enabled:
            return
        if self._fetching:          # previous request still running, skip this tick
            return
        self._fetching = True
        self.run_worker(self._fetch_vm_metrics, exclusive=True, thread=True)


    def set_status(self, slug: str, status: str) -> None:
        label = self.query_one(f"#status-{slug}", Label)
        label.update(status)
        label.styles.color = STATUS_COLOR[status]
    
    def _fetch_vm_metrics(self) -> None:
        try:
            if not self._polling_enabled:
                return
            cfg_mgr = self.app.config_manager
            cfg_mgr.load()
            rows: list[ServerInfo] = []
            errors: list[str] = []

            for host_config in cfg_mgr.config.hosts:
                if not self._polling_enabled:
                    return
                api = CallProxmox(app=self.app)

                for resource_type, path in (
                    ("VM", ProxmoxApiPaths.qemu(host_config.name)),
                    ("CT", ProxmoxApiPaths.lxc(host_config.name)),
                ):
                    if not self._polling_enabled:
                        return
                    try:
                        print("Logs", resource_type, path)
                        response = api.call_proxmox(path, host=host_config.address)
                        for resource in response.get("data", []):
                            if resource_type == "VM":
                                # vm_networking_response: QemuNetworkResponse = api.call_proxmox(path, host=host_config.address)
                                # print("Logs", vm_networking_response)
                                
                                typed_resource = ProxmoxVM.model_validate(resource)
                            else:
                                typed_resource = ProxmoxCT.model_validate(resource)
                            rows.append(self._format_metric_row(typed_resource))
                    except RuntimeError as error:
                        errors.append(f"{host_config.name}: {error}")

            if self._polling_enabled:
                self.app.call_from_thread(self._update_servers, rows, errors)
        except (OSError, ValueError, RuntimeError) as error:
            if self._polling_enabled:
                self.app.call_from_thread(self._update_servers, [], [str(error)])
        finally:
            self._fetching = False

    @staticmethod
    def _format_metric_row(resource: ProxmoxVM | ProxmoxCT) -> ServerInfo:
        if isinstance(resource, ProxmoxVM):
            name = resource.name or f"VM {resource.vmid}"
            type = f"VM {resource.vmid or '-'}"
        else:
            name = resource.display_name or f"CT {resource.vmid}"
            type = f"CT {resource.vmid or '-'}"

        status = str(resource.status or "Stopped").strip().lower().title()
        if status not in STATUS_COLOR:
            status = "Stopped"

        max_memory = resource.maxmem or 0
        memory_percent = int((resource.mem or 0) / max_memory * 100) if max_memory else 0
        total_ram = f"{max_memory / (1024 ** 3):.1f} GB" if max_memory else "-"
        uptime_seconds = resource.uptime
        if uptime_seconds is None:
            uptime = "-"
        else:
            days, remainder = divmod(int(uptime_seconds), 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes = remainder // 60
            uptime = f"{days}d {hours}h" if days else f"{hours}h {minutes}m" if hours else f"{minutes}m"

        return ServerInfo(
            id=int(resource.vmid or 0),
            name=name,
            type=type,
            status=status,
            cpu=(resource.cpu or 0) * 100,
            mem=memory_percent,
            total_ram=total_ram,
            uptime=uptime,
            node=getattr(resource, "node", None),
        )

    def _update_servers(self, servers: list[ServerInfo], errors: list[str]) -> None:
        if not self._polling_enabled:
            return
        self.servers = sorted(servers, key=lambda server: server.name.casefold())
        
        incoming = {slugify(server.name, server.id): server for server in self.servers}

        # update existing rows, drop rows that disappeared
        for row in list(self.query(ServerRow)):
            if row.slug in incoming:
                row.update_server(incoming.pop(row.slug))
            else:
                row.remove()

        # whatever is left is new
        for server in incoming.values():
            self.mount(ServerRow(server))
            
        if errors:
            self.notify("\n".join(errors), severity="warning")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""
        if not button_id or "-" not in button_id:
            return

        action, _, slug = button_id.partition("-")
        if action not in {"start", "shutdown", "restart"} or not slug:
            return

        server = next(
            (item for item in self.servers if slugify(item.name, item.id) == slug),
            None,
        )
        if server is None:
            self.notify("This server could not be found for the requested action.", severity="error")
            return

        resource_type = server.type.split()[0].lower()
        if resource_type == "vm":
            action_map = {
                "start": (ProxmoxApiPaths.start_vm, "Running", "started"),
                "shutdown": (ProxmoxApiPaths.shutdown_vm, "Stopped", "shut down"),
                "restart": (ProxmoxApiPaths.reboot_vm, "Restarting", "restarting…"),
            }
        elif resource_type == "ct":
            action_map = {
                "start": (ProxmoxApiPaths.start_ct, "Running", "started"),
                "shutdown": (ProxmoxApiPaths.shutdown_ct, "Stopped", "shut down"),
                "restart": (ProxmoxApiPaths.reboot_ct, "Restarting", "restarting…"),
            }
        else:
            self.notify(f"{server.name} has an unsupported resource type for actions.", severity="error")
            return

        path_builder, status, result_message = action_map[action]

        cfg_mgr = self.app.config_manager
        cfg_mgr.load()
        hosts = getattr(cfg_mgr.config, "hosts", [])
        node = server.node or (hosts[0].name if hosts else "")
        if not node:
            self.notify(f"{server.name} is missing a valid node for the requested action.", severity="error")
            return

        api = CallProxmox(app=self.app)

        try:
            response = api.call_proxmox(
                path_builder(node, server.id),
                httpMethod="post",
            )
        except RuntimeError as error:
            http_response = getattr(error.__cause__, "response", None)
            status_code = getattr(http_response, "status_code", None)
            detail = (
                f"HTTP {status_code}: {getattr(http_response, 'reason', '')}"
                if status_code is not None
                else str(error)
            )
            self.notify(f"{server.name} failed to {action}. Error: {detail}", severity="error")
            return

        if not isinstance(response, dict) or not response.get("data"):
            self.notify(
                f"{server.name} failed to {action}. Proxmox returned an unexpected response.",
                severity="error",
            )
            return

        self.set_status(slug, status)
        self.notify(f"{server.name} {result_message}", severity="warning" if action == "shutdown" else "information")
        if action == "restart":
            self.set_timer(1.5, lambda: self.set_status(slug, "Running"))
    