import sys
from pathlib import Path
from typing import Optional
from textual.app import App as TextualApp
import logging
import requests

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from services.token_store import TokenStore
from services.configuration import ConfigManager

logger = logging.getLogger(__name__)

class GetNodes:
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

    def get_nodes(self, host: Optional[str] = None, verify: Optional[bool] = False, api_token: Optional[str] = None) -> dict:
        cfg = self.getConfig()

        if host is None:
            conf = cfg.load()
            if not conf.hosts:
                raise RuntimeError("No configured hosts found; pass `host` explicitly")
            host = conf.hosts[0].address

        ticket = TokenStore().get_ticket_data("CSRFToken")        # should return the raw ticket string, e.g. 'PVE:root@pam:...::'
        csrf = TokenStore().get_ticket_data("AccessTicket")       # CSRFPreventionToken value

        if not ticket or not csrf:
            raise RuntimeError("No login ticket or CSRF token available; authenticate first")

        cookies = {"PVEAuthCookie": ticket}
        headers = {"CSRFPreventionToken": csrf}

        user_realm = conf.hosts[0].username  # Replace with your actual user/realm
        token_id = "Homelab-Token"   # Replace with your Token ID (e.g., from Datacenter > Permissions > API Tokens)
        secret = "71347159-af7f-4374-abc7-407df7f21826" # Your current secret
        
        token_value = f"PVEAPIToken={user_realm}!{token_id}={secret}"

        headers = {
            "Authorization": token_value
        }
        
        url = f"https://{host}:8006/api2/json/nodes"

        try:
            response = requests.get(url, headers=headers, verify=verify, timeout=15)
            # response = requests.get(url, headers=headers, cookies=cookies, verify=verify, timeout=15)
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
    resp = GetNodes()
    data = resp.get_nodes()
    print(data)