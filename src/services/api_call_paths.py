class ProxmoxApiPaths:
	"""Relative paths for the Proxmox JSON API.

	Pass the returned value to ``CallProxmox.call_proxmox``. Paths do not
	include the ``/api2/json/`` prefix, host, or authentication details.
	"""

	GET_TICKET = "access/ticket"
	VERSION = "version"
	NODES = "nodes"
	STORAGE = "storage"
	POOLS = "pools"
	CLUSTER = "cluster"

	@staticmethod
	def node(node: str) -> str:
		return f"nodes/{node}"

	@staticmethod
	def shutdown_ct(node: str, id: int | str) -> str:
		return f"nodes/{node}/lxc/{id}/status/shutdown"

	@staticmethod
	def start_ct(node: str, id: int | str) -> str:
		return f"nodes/{node}/lxc/{id}/status/start"

	@staticmethod
	def ct_status(node: str, id: int | str) -> str:
		return f"nodes/{node}/lxc/{id}/status/current"

	@staticmethod
	def reboot_ct(node: str, id: int | str) -> str:
		return f"nodes/{node}/lxc/{id}/status/reboot"

	@staticmethod
	def shutdown_vm(node: str, id: int | str) -> str:
		return f"nodes/{node}/qemu/{id}/status/shutdown"

	@staticmethod
	def start_vm(node: str, id: int | str) -> str:
		return f"nodes/{node}/qemu/{id}/status/start"

	@staticmethod
	def vm_status(node: str, id: int | str) -> str:
		return f"nodes/{node}/qemu/{id}/status/current"

	@staticmethod
	def reboot_vm(node: str, id: int | str) -> str:
		return f"nodes/{node}/qemu/{id}/status/reboot"

	@staticmethod
	def lxc(node: str, id: int | str | None = None) -> str:
		path = f"nodes/{node}/lxc"
		return path if id is None else f"{path}/{id}"

	@staticmethod
	def qemu(node: str, id: int | str | None = None) -> str:
		path = f"nodes/{node}/qemu"
		return path if id is None else f"{path}/{id}"

	@staticmethod
	def qemu_networking(node: str, id: int | str | None = None) -> str:
		return f"nodes/{node}/qemu/{id}/agent/network-get-interfaces"

	@staticmethod
	def zfs_scan(node: str) -> str:
		return f"nodes/{node}/scan/zfs"

	@staticmethod
	def pbs_scan(node: str) -> str:
		return f"nodes/{node}/scan/pbs"

	@staticmethod
	def zfs_disks(node: str) -> str:
		return f"nodes/{node}/disks/zfs"

	@staticmethod
	def directory_disks(node: str) -> str:
		return f"nodes/{node}/disks/directory"

	@staticmethod
	def lvm_disks(node: str) -> str:
		return f"nodes/{node}/disks/lvm"

	@staticmethod
	def qemu_monitor(node: str, id: int | str) -> str:
		return f"nodes/{node}/qemu/{id}/monitor"
