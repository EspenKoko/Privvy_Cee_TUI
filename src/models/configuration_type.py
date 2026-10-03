from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ServerConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    address: str
    port: int = 22
    username: str = "root"
    auth_method: str = "password"  # "password" or "ssh_key"
    ssh_key_path: Optional[str] = None
    is_hypervisor: bool = False
    # NOTE: no password field here on purpose — that lives in keyring only.

    @property
    def credential_key(self) -> str:
        """Unique lookup key for keyring, since keyring is just service+username -> secret."""
        return f"{self.name}:{self.username}"

    @property
    def host(self) -> str:
        return self.address

    @host.setter
    def host(self, value: str) -> None:
        self.address = value

    @property
    def isHost(self) -> bool:
        return self.is_hypervisor

    @isHost.setter
    def isHost(self, value: bool) -> None:
        self.is_hypervisor = bool(value)

    @classmethod
    def from_dict(cls, data: dict, default_is_hypervisor: Optional[bool] = None) -> "ServerConfig":
        address = data.get("address") or data.get("host")
        if address is None:
            raise ValueError("ServerConfig requires an address or host field")

        if default_is_hypervisor is None:
            is_hypervisor = data.get("is_hypervisor")
            if is_hypervisor is None:
                is_hypervisor = data.get("isHost", False)
        else:
            is_hypervisor = data.get("is_hypervisor", data.get("isHost", default_is_hypervisor))

        payload = {
            "name": data["name"],
            "address": address,
            "port": data.get("port", 22),
            "username": data.get("username", "root"),
            "auth_method": data.get("auth_method", "password"),
            "ssh_key_path": data.get("ssh_key_path"),
            "is_hypervisor": bool(is_hypervisor),
        }
        return cls(**payload)


class AppSettings(BaseModel):
    polling_rate_seconds: int = 5
    theme: str = "textual-dark"
    log_level: str = "INFO"


class AppConfig(BaseModel):
    hosts: list[ServerConfig] = Field(default_factory=list)
    servers: list[ServerConfig] = Field(default_factory=list)
    settings: AppSettings = Field(default_factory=AppSettings)