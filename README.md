# Privvy Cee TUI

A terminal-based homelab dashboard built with Python and Textual for monitoring hosts, VMs, containers, and system health from a lightweight TUI.

## Overview

Privvy Cee TUI provides a quick, keyboard-friendly view of your infrastructure with:
- Host resource monitoring
- VM status and health
- Container overview
- Network and storage metrics
- Local configuration persistence
- Windows Credential Manager integration for secure secrets storage

## Prerequisites

Before installing and running the app, make sure you have:

- Python 3.10 or newer
- Windows 10/11
- PowerShell

If you are using a virtual environment, activate it first:

```powershell
cd <Path to project>\Privvy_Cee_TUI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Restart your terminal session and run the app with
```powershell
PrivvyCee
```

## Getting started

### Standard run

From the project root:

```cmd
python -m main
```

### Development mode with live reload

```powershell
textual run --dev main
```

### Debug console

Open a separate terminal:

```powershell
textual console
```

Then run in another terminal

```powershell
textual run --dev main
```

## Exiting the TUI

Use:

```text
Ctrl + Q
```

## Configuration and storage

All application configuration is stored at in AppData and windows credential manager
**NB!** This file is very important as modifications or deletions in the file outside the app can result in isolated windows credentials that cannot be mapped back to the app

```text
%APPDATA%\Local\privvy_cee_tui
```

## Install and run

### Development run
From the project root, install the app in editable mode:

```powershell
cd <Path to project>\Privvy_Cee_TUI
py -3.10 -m pip install --upgrade pip
py -3.10 -m pip install --user --editable .
```

If `homelab` is not recognized, add the user Scripts folder to your PATH and reopen PowerShell:

```powershell
$env:Path += ";$env:APPDATA\Python\Python310\Scripts"
```

Then run the app from any directory:

```powershell
homelab
```

If you used a local virtual environment instead:

```powershell
cd <Path to project>\Privvy_Cee_TUI
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install --editable .
homelab
```

### Production exe file run

Add executable to the path once built

```powershell
$bin = "<Path to project>\Privvy_Cee_TUI\dist"
[Environment]::SetEnvironmentVariable(
  "Path",
  [Environment]::GetEnvironmentVariable("Path", "User") + ";$bin",
  "User"
)
```

## Build executable

To build the app as a one-folder executable and package it in an installer:

```powershell
./.github/scripts/build.ps1
```

To build the app as a single file:

```powershell
./.github/scripts/build-combined.ps1
```

## Documentation

Api documentation can be found in the `Proxmox.json`

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

## Contribution

Cover image source:

```text
Image: flaticon.com/free-icons/biometric-identification
```

This cover has been designed using resources from Flaticon.com.