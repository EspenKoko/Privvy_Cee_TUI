Getting started

## Setting up poetry
[install pipx](https://pipx.pypa.io/stable/how-to/install-pipx/#on-windows) if not already installed
```cmd
py -m pip install --user pipx
```

## Install Poetry if not already installed
[Install poetry](https://python-poetry.org/docs/#installation)
```cmd
pipx install poetry
```

## Configure poetry
```cmd
poetry config virtualenvs.in-project true
poetry install

python -m venv .venv # if needed
.venv\Scripts\Activate.ps1
poetry env info
```

## Install Textual
https://textual.textualize.io/getting_started/

```cmd
pip install textual textual-dev
```

To exit the tui 

```
ctrl+q
```

To live update during debug
run the app module or the package entrypoint with Textual's dev runner:
```
.venv\Scripts\textual.exe run --dev main
```

Or run the app normally:
```
python -m main

<!-- When running as a module make sure you are in the module package's root -->
python -m privvy_cee_ui.metrics.more_metrics

```

to live debug
```powershell
textual run --dev main
```

in seporate terminal run
```powershell
textual console
```

All server config is saved to C:\Users\espen.koko\AppData\Local\privvy_cee_ui
and the passwords are saved to windows crednetial manager


┌──────────────────────────────────────────────────────────────────────────────┐
│ Homelab Dashboard                                   Connected ● 22:14:03     │
├──────────────────────────────────────────────────────────────────────────────┤
│ HOST: Proxmox-01                                                     Healthy │
│ CPU  18% ████░░░░░░░░░░░░                                              8 /16 │
│ RAM  42% ████████░░░░░░░                                            13 /32GB │
│ Disk 61% ███████████░░░░                                         610 /1TB    │
│ Network ↓ 38MB/s ↑ 4MB/s          Uptime 18d 03h      Temp 48°C            │
└──────────────────────────────────────────────────────────────────────────────┘

┌────────────── Virtual Machines ──────────────────────────────────────────────┐
│ Name                 Status      CPU     RAM        IP              Uptime   │
├──────────────────────────────────────────────────────────────────────────────┤
│▶ Windows Server      Running      8%     3.4GB      10.0.0.10       14d      │
│ Ubuntu Docker        Running      2%     900MB      10.0.0.11       22d      │
│ Home Assistant       Running      5%     2.1GB      10.0.0.15       18d      │
│ Kali                 Stopped      -       -         -               -        │
└──────────────────────────────────────────────────────────────────────────────┘

┌────────────── Containers ────────────────────────────────────────────────────┐
│ Name             Status      CPU      RAM      Image              Health      │
├──────────────────────────────────────────────────────────────────────────────┤
│▶ Jellyfin        Running      6%      1.2GB    jellyfin:latest    Healthy    │
│ Grafana          Running      1%      220MB    grafana            Healthy    │
│ Prometheus       Running      3%      350MB    prom/prometheus    Healthy    │
│ Vaultwarden      Running      0%      90MB     vaultwarden        Healthy    │
└──────────────────────────────────────────────────────────────────────────────┘

Alerts
────────────────────────────────────────────────────────────────────────────────
• None


┌─────────────────────────────────────────────────────────────────────────────┐
│ Host: Proxmox-01                                           Connected ●       │
├─────────────────────────────────────────────────────────────────────────────┤

CPU
─────────────────────────────────────────────────────────────────────────────
Usage          18%
Temperature    48°C
Frequency      4.8GHz
Sockets        1
Cores          8
Threads        16
Load Avg       1.8 1.4 1.2

Per-Core Usage

Core0   ████████████ 42%
Core1   ███ 11%
Core2   ███████ 26%
Core3   ██████████ 38%
...

Memory

Used        13GB
Free        19GB
Swap        512MB

Disk

nvme0n1

Usage       61%
Read        110MB/s
Write       18MB/s
IOPS        300

Network

eth0

Download    38MB/s
Upload      4MB/s
Errors      0
Packets/s   2450

Temperatures

CPU      48°C
NVME     42°C

┌─────────────────────────────────────────────────────────────────────────────┐
│ Ubuntu Docker VM                                            Running ●        │
├─────────────────────────────────────────────────────────────────────────────┤

General

ID             102
Host           Proxmox-01
OS             Ubuntu Server 24.04
IP             10.0.0.11
Uptime         22 days

Resources

vCPUs          4
CPU Usage      8%

Memory         8GB
Used           2.4GB

Disk

VirtIO
Used           42GB / 100GB

Network

Receive        4MB/s
Transmit       900KB/s

Snapshots

• clean-install
• before-update

Recent Events

22:11 Backup Completed
18:30 apt update
Yesterday Reboot

┌──────────────────────────────────────────────────────────────────────────────┐
│ Jellyfin Container                                        Running ●          │
├──────────────────────────────────────────────────────────────────────────────┤

General

Container ID     210
Image            jellyfin:latest
Version          10.10

CPU

Usage            6%
Limits           4 cores

Memory

Limit            4GB
Used             1.2GB

Disk

Writable Layer   900MB
Volumes          3

Network

IP               10.0.0.25
RX               2MB/s
TX               400KB/s

Ports

8096
8920

Volumes

/media
/config
/cache

Logs

[INFO] ...
[INFO] ...