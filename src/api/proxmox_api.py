import os
from pathlib import Path
from dotenv import load_dotenv
        
ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env")

from proxmoxer import ProxmoxAPI

user=os.getenv("PVE_USER")
token=os.getenv("PVE_TOKEN", "")
tokenID=os.getenv("PVE_TOKEN_ID", "")
password=os.getenv("PVE_PASS")
        
proxmox = ProxmoxAPI(
    "192.168.1.10",
    user=f'{user}@pve',
    token_name=tokenID,
    token_value=token,
    verify_ssl=False,   # Proxmox uses a self-signed cert by default
    port=8006,
)

# List all nodes (usually just one in a homelab)
nodes = proxmox.nodes.get()
node_name = nodes[0]["node"]  # e.g. "proxmox-01"

# Host-level stats
status = proxmox.nodes(node_name).status.get()
print(status["cpu"])            # fraction, e.g. 0.18 (multiply by 100)
print(status["memory"]["used"]) # bytes
print(status["memory"]["total"])
print(status["uptime"])         # seconds

# All VMs on that node
vms = proxmox.nodes(node_name).qemu.get()
for vm in vms:
    print(vm["name"], vm["status"], vm["cpu"], vm["mem"])

# All LXC containers
containers = proxmox.nodes(node_name).lxc.get()
for ct in containers:
    print(ct["name"], ct["status"], ct["cpu"], ct["mem"])