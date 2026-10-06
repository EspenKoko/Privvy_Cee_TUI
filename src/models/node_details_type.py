from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class NodeNetworkInterface(BaseModel):
    model_config = ConfigDict(extra="ignore")

    iface: str
    exists: int | None = None
    families: list[str] = Field(default_factory=list)
    type: str | None = None
    method: str | None = None
    active: int | None = None
    method6: str | None = None
    altnames: list[str] = Field(default_factory=list)
    priority: int | None = None
    address: str | None = None
    netmask: str | None = None
    bridge_fd: str | None = None
    autostart: int | None = None
    cidr: str | None = None
    gateway: str | None = None
    bridge_ports: str | None = None
    bridge_stp: str | None = None


class NodeNetworkResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    data: list[NodeNetworkInterface] = Field(default_factory=list)


class NodeCpuInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    cores: int | None = None
    family: str | None = None
    sockets: int | None = None
    flags: str | None = None
    cpus: int | None = None
    hvm: str | None = None
    vendor: str | None = None
    mhz: str | None = None
    user_hz: int | None = None
    model: str | None = None


class NodeResourceStatus(BaseModel):
    model_config = ConfigDict(extra="ignore")

    free: int = 0
    total: int = 0
    used: int = 0
    available: int | None = None
    avail: int | None = None


class NodeSwapStatus(BaseModel):
    model_config = ConfigDict(extra="ignore")

    free: int = 0
    used: int = 0
    total: int = 0


class NodeKsmStatus(BaseModel):
    model_config = ConfigDict(extra="ignore")

    shared: int = 0


class NodeBootInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    secureboot: int | None = None
    mode: str | None = None


class NodeKernelInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    version: str | None = None
    machine: str | None = None
    release: str | None = None
    sysname: str | None = None


class NodeStatusData(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    uptime: int = 0
    cpu: float = 0.0
    cpuinfo: NodeCpuInfo | None = None
    ksm: NodeKsmStatus | None = None
    boot_info: NodeBootInfo | None = Field(default=None, alias="boot-info")
    pveversion: str | None = None
    swap: NodeSwapStatus | None = None
    kversion: str | None = None
    wait: float | None = None
    idle: float | None = None
    loadavg: list[str] = Field(default_factory=list)
    memory: NodeResourceStatus = Field(default_factory=NodeResourceStatus)
    rootfs: NodeResourceStatus = Field(default_factory=NodeResourceStatus)
    current_kernel: NodeKernelInfo | None = Field(default=None, alias="current-kernel")


class NodeStatusResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    data: NodeStatusData