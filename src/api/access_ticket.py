import json
import os
from pathlib import Path

import requests


ROOT_DIR = Path(__file__).resolve().parents[2]
TICKET_PATH = ROOT_DIR / "access_ticket.json"


def fetch_access_ticket(username: str, password: str, host: str = "192.168.1.10", port: int = 8006) -> dict:
    response = requests.post(
        f"https://{host}:{port}/api2/json/access/ticket",
        data={"username": username, "password": password},
        verify=False,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def save_access_ticket(ticket_data: dict, path: str | None = None) -> Path:
    target_path = Path(path or TICKET_PATH)
    target_path.write_text(json.dumps(ticket_data, indent=2), encoding="utf-8")
    return target_path


def load_access_ticket(path: str | None = None) -> dict:
    target_path = Path(path or TICKET_PATH)
    if not target_path.exists():
        raise FileNotFoundError(f"No saved ticket found at {target_path}")
    return json.loads(target_path.read_text(encoding="utf-8"))


def get_ticket_value(path: str | None = None) -> str:
    data = load_access_ticket(path)
    return data.get("data", {}).get("ticket", "")


def get_csrf_token(path: str | None = None) -> str:
    data = load_access_ticket(path)
    return data.get("data", {}).get("CSRFPreventionToken", "")


if __name__ == "__main__":
    ticket_data = fetch_access_ticket("Privvy_Cee_User@pve", "Pr1vvyC3380085")
    save_access_ticket(ticket_data)
    print("Saved ticket to", TICKET_PATH)
    print(get_ticket_value())