from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ProxmoxVM(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    vmid: int
    name: str
    status: str
    cpu: float = 0.0
    mem: int = 0
    maxmem: int = 0
    uptime: Optional[int] = None
    node: Optional[str] = None

    @property
    def cpu_percent(self) -> float:
        return self.cpu * 100.0

    @property
    def memory_percent(self) -> float:
        if self.maxmem <= 0:
            return 0.0
        return min(self.mem / self.maxmem, 1.0)