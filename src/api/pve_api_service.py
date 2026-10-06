import sys
from pathlib import Path
from typing import Literal, Optional
from textual.app import App as TextualApp
import logging
import requests

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.services.configuration import ConfigManager

logger = logging.getLogger(__name__)
HttpMethod = Literal["get", "post", "delete", "put"]

class CallProxmox:
    def __init__(self, app: Optional[TextualApp] = None) -> None:
        # Prefer an injected textual App so we reuse its `config_manager`.
        if app is not None:
            self.app = app
        else:
            try:
                self.app = TextualApp.get_running_app()
            except Exception:
                self.app = None

    def getConfig(self) -> ConfigManager:
        # If this class is used inside the textual app, `self.app.config_manager`
        # will be available. When used standalone, return a new ConfigManager.
        if hasattr(self, "app") and getattr(self.app, "config_manager", None) is not None:
            return self.app.config_manager
        return ConfigManager()

    def call_proxmox(
            self
            , path: str
            , httpMethod: HttpMethod = "get"
            , host: Optional[str] = None
            , verify: Optional[bool] = False
        ) -> dict:
        httpMethod = httpMethod.lower()
        if httpMethod not in {"get", "post", "delete", "put"}:
            raise ValueError(
                f"Unsupported HTTP method: {httpMethod}. "
                "Choose get, post, delete, or put."
            )

        cfg = self.getConfig()
        conf = cfg.load()

        if host is None:
            if not conf.hosts:
                raise RuntimeError("No configured hosts found; pass `host` explicitly")
            host = conf.hosts[0].address

        user_realm = conf.hosts[0].username
        token_id = "Homelab-Token"
        secret = "7228eeb2-169c-45a0-ba4f-72d3b66efcdd"
        
        token_value = f"PVEAPIToken={user_realm}!{token_id}={secret}"

        headers = {
            "Authorization": token_value
        }
        
        url = f"https://{host}:8006/api2/json/{path}"

        try:
            match httpMethod:
                case "get":
                    response = requests.get(url, headers=headers, verify=verify, timeout=15)
                case "post":
                    response = requests.post(url, headers=headers, verify=verify, timeout=15) #Add body if needed
                case "put":
                    response = requests.put(url, headers=headers, verify=verify, timeout=15)
                case "delete":
                    response = requests.delete(url, headers=headers, verify=verify, timeout=15)
                    
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.exception("Failed to fetch nodes from %s", host)
            raise RuntimeError(f"Failed to fetch nodes from {host}") from e

        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            try:
                return response.json()
            except ValueError as e:
                logger.exception("Invalid JSON from %s", host)
                raise RuntimeError("Invalid JSON response from PVE API") from e
        return response.text

if __name__ == "__main__":
    resp = CallProxmox()
    data = resp.call_proxmox()
    print(data)