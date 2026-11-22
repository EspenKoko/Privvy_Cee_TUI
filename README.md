# Privvy Cee TUI

A keyboard-friendly terminal dashboard for monitoring your homelab. Privvy Cee TUI currently connects to Proxmox VE to display host, virtual machine, container, and system health information.

## What it does

- Shows host resource, network, and storage metrics.
- Displays virtual machine and container status.
- Saves application configuration in your user configuration directory.
- Stores credentials using your operating system's keyring.

Support for other Linux environments is planned.

## Contents

- [Requirements](#requirements)
- [Install and run](#install-and-run)
- [Production](#Production)
- [Configuration and credentials](#configuration-and-credentials)
- [Development](#Development)
- [Documentation](#documentation)
- [Example dashboard](#example-dashboard)
- [Credits](#credits)

## Requirements

- A Proxmox VE host reachable from the computer running the app.
- Windows or Linux. Ubuntu on WSL can use the Linux instructions below; make sure the WSL environment can reach your Proxmox host and VPN.

## Production

### Build executable with installer

#### Windows Install
To build the app as a one-folder executable and package it in an installer:
**NB!** requires Inno 6

```shell
./build.ps1
```

### Build the app as a standalone file:

```shell
./build-standalone-app.ps1
```

**Add path if not using the installer**

Output will be in `installer-output\PrivvyCeeTUIsetup.exe`

```shell
$bin = "<Path to project>\Privvy_Cee_TUI\dist" # Or path to the standalone exe
[Environment]::SetEnvironmentVariable(
  "Path",
  [Environment]::GetEnvironmentVariable("Path", "User") + ";$bin",
  "User"
)
```

#### Linux

Go to the installed folder and run this command to pull the setup script and run interactively
```bash
cd /path/to/extracted-bundle
curl -fsSL -o /tmp/privvycee-setup.sh \
  https://raw.githubusercontent.com/EspenKoko/Privvy_Cee_TUI/develop/privvycee-setup.sh
bash /tmp/privvycee-setup.sh
```

To view app credentials/secrets
```bash
secret-tool search --all service PrivvyCeeTui
secret-tool search --all service PrivvyCeeToken
```

To view all credentials/secrets
```bash
secret-tool search --all application "Python keyring library"

```


Once completed from any directory/terminal on the pc run `privvycee` to open the app in a terminal

---

## Configuration and storage

All application configuration for windows is stored at in AppData and Windows credential manager and for linux in `- ~/.local/share/keyrings/Default.keyring`
**NB!** The config files are very important. Modifications or deletions in the file outside the app can result in isolated credentials that cannot be mapped back to the app

**For windows:**
- %APPDATA%\Local\privvy_cee_tui\config.toml

**For Linux:**
- ~/.config/privvy_cee_tui/config.toml

---

## Development

### Windows

**Prerequisites**
- Python 3.10 or newer

If you are using a virtual environment, activate it first:
```shell
cd <Path to project>\Privvy_Cee_TUI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Linux

**Prerequisites**
- Python 3.10 or newer
- compatible keyring package for your OS

If you are using a virtual environment, activate it first:
```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install keyring # for os keyring
```

#### Debian

```bash
sudo apt update && sudo apt install gnome-keyring -y
```

If using a headless system
```bash
sudo apt update && sudo apt install dbus-x11
# Ensure the keyrings directory exists
mkdir -p ~/.local/share/keyrings
```

Start the secrets component of gnome-keyring-daemon if not done automatically after app run
```bash
eval $(echo -n "your_keyring_password" | gnome-keyring-daemon --start --unlock --components=secrets)
```

To view encrypted file direcly
```bash
python -c "
import secretstorage
conn = secretstorage.dbus_init()
for col in secretstorage.get_all_collections(conn):
    print(f'=== Collection: {col.get_label()} ===')
    for item in col.get_all_items():
        print(f'Label: {item.get_label()} | Attrs: {item.get_attributes()} | Secret: {item.get_secret().decode()}')
"
```

OR

Install libsecret-tools to view in terminal
```bash
sudo apt install libsecret-tools -y
secret-tool search --all service PrivvyCeeTui
secret-tool search --all service PrivvyCeeToken
```

To view all secrets
```bash
secret-tool search --all application "Python keyring library"

```

#### Arch 
<!-- TODO -->

### Standard run

From the project root:

```shell
python -m main
```

### Development mode with live reload

Open a second terminal and start the console:

```shell
textual console
```

Then run the app in the first terminal:

```shell
textual run --dev main
```

### Development run with path setup
From the project root, install the app in editable mode:
Config taken from `pyproject.toml`

If encoutering errors when running
```shell
python -m pip install --user pipx
python -m pipx ensurepath
```

**Install the project in the current folder**

If using a venv
```shell
cd <Path to project>\Privvy_Cee_TUI
python -m pip install --editable . 
```

If not using a venv **not recommended**
```shell
cd <Path to project>\Privvy_Cee_TUI
python -m pip install --user --editable .
```

If `homelab` is not recognized, add the user Scripts folder to your PATH and reopen shell:

```shell
$env:Path += ";$env:APPDATA\Python\Python310\Scripts"
```

Then run the app from any directory:

```shell
homelab
```

#### Uninstall the app

```shell
python -m pip uninstall homelab
```

---

## Documentation

The Proxmox API reference used by the project is in [`Proxmox.json`](Proxmox.json).

## Example dashboard

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Homelab Dashboard                                   Connected ● 22:14:03     │
├──────────────────────────────────────────────────────────────────────────────┤
│ HOST: Proxmox-01                                                     Healthy │
│ CPU  18% ████░░░░░░░░░░░░                                              8 /16 │
│ RAM  42% ████████░░░░░░░                                            13 /32GB │
│ Disk 61% ███████████░░░░                                         610 /1TB    │
│ Network ↓ 38MB/s ↑ 4MB/s          Uptime 18d 03h      Temp 48°C              │
└──────────────────────────────────────────────────────────────────────────────┘

┌────────────── Virtual Machines ──────────────────────────────────────────────┐
│ Name                 Status      CPU     RAM        IP              Uptime   │
├──────────────────────────────────────────────────────────────────────────────┤
│▶ Windows Server      Running      8%     3.4GB      10.0.0.10       14d     │
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
```

## Credits

Cover image source: [Biometric identification icons](https://www.flaticon.com/free-icons/biometric-identification) from Flaticon.
