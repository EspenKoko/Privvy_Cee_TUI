import os
import sys
from pathlib import Path
from typing import Optional
from textual.app import App as TextualApp
import requests
import logging
import keyring

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

dotenv_path = ROOT_DIR.parent / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)
else:
    # allow python-dotenv to search parent directories if layout differs
    load_dotenv()

from src.services.configuration import ConfigManager
from src.models.keyring_data import ServiceNames, ServiceTicketNames

logger = logging.getLogger(__name__)

DEFAULT_HOST = os.getenv("PVE_HOST", "127.0.0.1")

DEFAULT_USER = os.getenv("PVE_USER")
DEFAULT_PASSWORD = os.getenv("PVE_PASS")

class PVEAuthentication:
    SERVICE_NAME = ServiceNames.TOKEN_SERVICE
    
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

    def fetch_access_ticket(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        verify: Optional[bool] = False,
    ) -> dict:
        cfg = self.getConfig()

        if host is None:
            # When the file is run directly as a module, default to a known host.
            # Otherwise, if the app is running normally, use configured hosts.
            if __name__ == "__main__":
                host = DEFAULT_HOST
            else:
                conf = cfg.load()
                if not conf.hosts:
                    raise RuntimeError("No configured hosts found; pass `host` explicitly")
                host = conf.hosts[0].address

        if username is None:
            username = DEFAULT_USER

        if password is None:
            password = DEFAULT_PASSWORD

        try:
            response = requests.post(
                f"https://{host}:8006/api2/json/access/ticket",
                data={"username": username, "password": password},
                verify=verify,
                timeout=15,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.exception("Failed to fetch access ticket from %s", host)
            raise RuntimeError(f"Failed to fetch access ticket from {host}") from e

        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            try:
                return response.json()
            except ValueError as e:
                logger.exception("Invalid JSON from %s", host)
                raise RuntimeError("Invalid JSON response from PVE API") from e
        return response.text

    # TODO Vefity the token 

    def save_access_ticket(self, ticket_data: dict):
        response_data = ticket_data.get("data", {})
        for ticket_name in ServiceTicketNames:
            token = response_data.get(ticket_name.response_field)
            if not token:
                logger.warning("No %s found in ticket_data", ticket_name.response_field)
                continue
            self.save_ticket_data(ticket_name.keyring_name, token)

    def save_ticket_data(self, name: str, token: str) -> None:
        """Save token to keyring; if that fails, write encrypted file."""
        try:
            keyring.set_password(self.SERVICE_NAME, name, token)
            return
        except Exception:
            pass
        
    def get_ticket_value(self, name: str) -> str:
        """Retrieve token from keyring, or decrypt fallback file."""
        try:
            token = keyring.get_password(self.SERVICE_NAME, name)
            if token:
                return token
        except Exception:
            pass
        
    def delete_tokens(self) -> None:
        """Remove all registered tickets from keyring."""
        for ticket_name in ServiceTicketNames:
            try:
                keyring.delete_password(self.SERVICE_NAME, ticket_name.keyring_name)
            except keyring.errors.PasswordDeleteError:
                pass

    def authenticate(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        verify: Optional[bool] = False,
    ):
        # Use instance methods rather than a global `auth` variable.
        ticket_data = self.fetch_access_ticket(username=username, password=password, host=host, verify=verify)
        self.save_access_ticket(ticket_data)
        return ticket_data

if __name__ == "__main__":
    auth = PVEAuthentication()
    ticket_data = auth.fetch_access_ticket()
    auth.save_access_ticket(ticket_data)
    print("Saved ticket")
    print(auth.get_ticket_value())