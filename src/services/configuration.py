from __future__ import annotations
from pathlib import Path
from typing import Optional
try:
    import tomllib  # stdlib, Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib  # backport for 3.10 and earlier
import tomli_w
import keyring
import platformdirs

from src.models.configuration_type import ServerConfig, AppConfig, AppSettings

APP_NAME = "privvy_cee_tui"
KEYRING_SERVICE = "PrivvyCeeTui"  # namespace for all our keyring entries


def _strip_none(obj):
    """Recursively remove keys whose value is None, since TOML has no null type."""
    if isinstance(obj, dict):
        return {k: _strip_none(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [_strip_none(v) for v in obj]
    return obj


class ConfigManager:
    """
    Roughly the Python equivalent of binding IConfiguration to a POCO,
    except we own the read/write path explicitly instead of DI doing it for us.
    """

    def __init__(self):
        # Saves to C:\Users\espen.koko\AppData\Local\privvy_cee_ui
        config_dir = Path(platformdirs.user_config_dir(APP_NAME, appauthor=False))
        config_dir.mkdir(parents=True, exist_ok=True)
        self.config_path = config_dir / "config.toml"
        self.config: AppConfig = AppConfig()

    def is_first_run(self) -> bool:
        return not self.config_path.exists()

    def load(self) -> AppConfig:
        with open(self.config_path, "rb") as f:
            raw = tomllib.load(f)

        hypervisor_raw = raw.get("hosts", [])
        server_raw = raw.get("servers", [])

        hosts = [ServerConfig.from_dict(s, default_is_hypervisor=True) for s in hypervisor_raw]
        servers = [ServerConfig.from_dict(s, default_is_hypervisor=False) for s in server_raw]
        settings_raw = raw.get("settings", {})
        settings = AppSettings(**settings_raw)

        self.config = AppConfig(hosts=hosts, servers=servers, settings=settings)
        return self.config

    def save(self) -> None:
        data = {
            "hosts": [s.model_dump(mode="python") for s in self.config.hosts],
            "servers": [s.model_dump(mode="python") for s in self.config.servers],
            "settings": self.config.settings.model_dump(mode="python"),
        }
        data = _strip_none(data)  # drop None fields before writing, since TOML has no null
        with open(self.config_path, "wb") as f:
            tomli_w.dump(data, f)

    # --- Credential handling (never touches the TOML file) ---

    def set_password(self, server: ServerConfig, password: str) -> None:
        keyring.set_password(KEYRING_SERVICE, server.credential_key, password)

    def get_password(self, server: ServerConfig) -> Optional[str]:
        return keyring.get_password(KEYRING_SERVICE, server.credential_key)

    def delete_password(self, server: ServerConfig) -> None:
        try:
            keyring.delete_password(KEYRING_SERVICE, server.credential_key)
        except keyring.errors.PasswordDeleteError:
            pass  # already gone, that's fine

    def add_server(self, serverConfig: ServerConfig, password: Optional[str] = None) -> None:
        if serverConfig.is_hypervisor:
            self.config.hosts.append(serverConfig)
        else:
            self.config.servers.append(serverConfig)

        if password:
            self.set_password(serverConfig, password)
        self.save()

    def remove_server(self, server_name: str) -> None:
        server = next((s for s in self.config.servers if s.name == server_name), None)
        if server:
            self.delete_password(server)
            self.config.servers.remove(server)
            self.save()

    def delete_all_data(self) -> None:
        for server in [*self.config.hosts, *self.config.servers]:
            self.delete_password(server)

        self.config_path.unlink(missing_ok=True)
        self.config = AppConfig()