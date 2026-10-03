from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import DataTable, Static

from src.api.pve_api_service import CallProxmox
from src.models.lxc_type import ProxmoxCT
from src.models.qemu_type import ProxmoxVM
from src.services.api_call_paths import ProxmoxApiPaths
from src.models.qemu_networking_type import QemuNetworkResponse

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

    def compose(self) -> ComposeResult:
        yield DataTable(id="vm_table")
        yield DataTable(id="container_table")
        yield Static("Alerts\n• None", id="alerts")

    def on_mount(self) -> None:
        vm_table = self.query_one("#vm_table", DataTable)
        vm_table.add_columns("Name", "Status", "CPU", "RAM USAGE", "TOTAL RAM", "IP", "Uptime")
        self.refresh_data()
        # self.set_interval(3, self.refresh_data)

    def refresh_data(self) -> None:
        self.run_worker(self._fetch_vm_metrics, exclusive=True, thread=True)

    def _fetch_vm_metrics(self) -> None:
        cfg_mgr = self.app.config_manager
        rows = []
        errors = []

        for host_config in cfg_mgr.config.hosts:
            api = CallProxmox(app=self.app)

            for resource_type, path in (
                ("VM", ProxmoxApiPaths.qemu(host_config.name)),
                ("CT", ProxmoxApiPaths.lxc(host_config.name)),
            ):
                try:
                    print("Logs", resource_type, path)
                    
                        
                    response = api.call_proxmox(path, host=host_config.address)
                    for resource in response.get("data", []):
                        if resource_type == "VM":
                            vm_networking_response: QemuNetworkResponse = api.call_proxmox(path, host=host_config.address)
                            print("Logs", vm_networking_response)
                            
                            typed_resource = ProxmoxVM.model_validate(resource)
                        else:
                            typed_resource = ProxmoxCT.model_validate(resource)
                        rows.append(self._format_metric_row(resource_type, typed_resource))
                except RuntimeError as error:
                    errors.append(f"{host_config.name}: {error}")

        self.app.call_from_thread(self._update_metric_table, rows, errors)

    @staticmethod
    def _format_metric_row(resource_type: str, resource: ProxmoxVM | ProxmoxCT) -> tuple[str, ...]:
        if isinstance(resource, ProxmoxVM):
            max_memory = resource.maxmem or 0
            memory = resource.mem or 0
            memory_text = f"{memory / max_memory:.0%}" if max_memory else "-"
            max_memory = max_memory/ (1024 * 1024 * 1024)
            cpu_text = f"{(resource.cpu or 0) * 100:.1f}%"
            uptime = resource.uptime
            uptime_text = f"{int(uptime) // 86400}d" if uptime is not None else "-"
            return (
                f"{resource_type} {resource.vmid}: {resource.name}",
                str(resource.status),
                cpu_text,
                memory_text,
                max_memory,
                str(resource.node or "-"),
                uptime_text,
            )
            
        if isinstance(resource, ProxmoxCT):
            max_memory = resource.maxmem or 0
            memory = resource.mem or 0
            memory_text = f"{memory / max_memory:.0%}" if max_memory else "-"
            max_memory = max_memory/ (1024 * 1024 * 1024)
            cpu_text = f"{(resource.cpu or 0) * 100:.1f}%"
            uptime = resource.uptime
            uptime_text = f"{int(uptime) // 86400}d" if uptime is not None else "-"
            return (
                f"{resource_type} {resource.vmid or '-'}: {resource.display_name}",
                str(resource.status or "unknown"),
                cpu_text,
                memory_text,
                max_memory,
                str(resource.node or "-"),
                uptime_text,
            )

    def _update_metric_table(
        self,
        rows: list[tuple[str, ...]],
        errors: list[str],
    ) -> None:
        self._refresh_table(rows)
        alert_text = "Alerts\n• " + ("\n• ".join(errors) if errors else "None")
        self.query_one("#alerts", Static).update(alert_text)

    def _refresh_table(self, rows: list[tuple[str, ...]] | None = None) -> None:
        vm_table = self.query_one("#vm_table", DataTable)
        vm_table.clear()
        for row in rows or []:
            vm_table.add_row(*row)