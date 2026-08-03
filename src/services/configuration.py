from __future__ import annotations
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional
try:
    import tomllib  # stdlib, Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib  # backport for 3.10 and earlier
import tomli_w
import keyring
import platformdirs

APP_NAME = "privvy_cee_tui"
KEYRING_SERVICE = "privvy_cee_tui"  # namespace for all our keyring entries


def _strip_none(obj):
    """Recursively remove keys whose value is None, since TOML has no null type."""
    if isinstance(obj, dict):
        return {k: _strip_none(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [_strip_none(v) for v in obj]
    return obj


@dataclass
class ServerConfig:
    name: str
    host: str
    port: int = 22
    username: str = "root"
    auth_method: str = "password"  # "password" or "ssh_key"
    ssh_key_path: Optional[str] = None
    # NOTE: no password field here on purpose — that lives in keyring only.

    @property
    def credential_key(self) -> str:
        """Unique lookup key for keyring, since keyring is just service+username -> secret."""
        return f"{self.name}:{self.username}"


@dataclass
class AppSettings:
    polling_rate_seconds: int = 5
    theme: str = "textual-dark"
    log_level: str = "INFO"


@dataclass
class AppConfig:
    servers: list[ServerConfig] = field(default_factory=list)
    settings: AppSettings = field(default_factory=AppSettings)


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

        servers = [ServerConfig(**s) for s in raw.get("servers", [])]
        settings_raw = raw.get("settings", {})
        settings = AppSettings(**settings_raw)

        self.config = AppConfig(servers=servers, settings=settings)
        return self.config

    def save(self) -> None:
        data = {
            "servers": [asdict(s) for s in self.config.servers],
            "settings": asdict(self.config.settings),
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

    def add_server(self, server: ServerConfig, password: Optional[str] = None) -> None:
        self.config.servers.append(server)
        if password:
            self.set_password(server, password)
        self.save()

    def remove_server(self, server_name: str) -> None:
        server = next((s for s in self.config.servers if s.name == server_name), None)
        if server:
            self.delete_password(server)
            self.config.servers.remove(server)
            self.save()