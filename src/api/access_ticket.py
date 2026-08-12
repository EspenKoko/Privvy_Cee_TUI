import sys
from pathlib import Path
from typing import Optional
from textual.app import App as TextualApp
import requests

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from services.token_store import TokenStore
from services.configuration import ConfigManager, ServerConfig, AppSettings


class AuthenticateAgainstHost:

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

    def fetch_access_ticket(self, username: str, password: str, host: Optional[str] = None, port: int = 8006) -> dict:
        cfg = self.getConfig()
        if host is None:
            conf = cfg.load()
            if not conf.hosts:
                raise RuntimeError("No configured hosts found; pass `host` explicitly")
            host = conf.hosts[0].address

        response = requests.post(
            f"https://{host}:{port}/api2/json/access/ticket",
            data={"username": username, "password": password},
            verify=False,
            timeout=15,
        )
        response.raise_for_status()
        return response.json()

    def save_access_ticket(self, ticket_data: dict):
        token = ticket_data.get("data", {}).get("CSRFPreventionToken", "")
        TokenStore().save_token(token)

    def get_ticket_value(self) -> str:
        return TokenStore().get_token()

if __name__ == "__main__":
    auth = AuthenticateAgainstHost()
    ticket_data = auth.fetch_access_ticket("Privvy_Cee_User@pve", "Pr1vvyC3380085")
    auth.save_access_ticket(ticket_data)
    print("Saved ticket")
    print(auth.get_ticket_value())