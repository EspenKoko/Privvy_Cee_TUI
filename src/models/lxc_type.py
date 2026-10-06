from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict

class ProxmoxCT(BaseModel):
    model_config = ConfigDict(extra="ignore")

    vmid: Optional[int] = None
    name: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    cpu: Optional[float] = None
    mem: Optional[int] = None
    maxmem: Optional[int] = None
    swap: Optional[int] = None
    maxswap: Optional[int] = None
    disk: Optional[int] = None
    maxdisk: Optional[int] = None
    uptime: Optional[int] = None
    netin: Optional[int] = None
    netout: Optional[int] = None
    diskread: Optional[int] = None
    diskwrite: Optional[int] = None
    cpus: Optional[int] = None
    tags: Optional[str] = None
    pid: Optional[int] = None
    node: Optional[str] = None

    pressurecpufull: Optional[str] = None
    pressurecpusome: Optional[str] = None
    pressurememoryfull: Optional[str] = None
    pressurememorysome: Optional[str] = None
    pressureiofull: Optional[str] = None
    pressureiosome: Optional[str] = None

    @property
    def display_name(self) -> str:
        return self.name or "-"


class LxcListResponse(BaseModel):
    data: list[ProxmoxCT]