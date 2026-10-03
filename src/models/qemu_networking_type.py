from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class NetworkStatistic(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    tx_dropped: int = Field(default=0, alias="tx-dropped")
    rx_dropped: int = Field(default=0, alias="rx-dropped")
    tx_packets: int = Field(default=0, alias="tx-packets")
    rx_errs: int = Field(default=0, alias="rx-errs")
    rx_packets: int = Field(default=0, alias="rx-packets")
    tx_errs: int = Field(default=0, alias="tx-errs")
    tx_bytes: int = Field(default=0, alias="tx-bytes")
    rx_bytes: int = Field(default=0, alias="rx-bytes")


class IPAddress(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    ip_address: str = Field(alias="ip-address")
    prefix: int
    ip_address_type: str = Field(alias="ip-address-type")


class NetworkInterface(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    hardware_address: Optional[str] = Field(default=None, alias="hardware-address")
    statistics: Optional[NetworkStatistic] = None
    ip_addresses: list[IPAddress] = Field(default_factory=list, alias="ip-addresses")


class QemuNetworkData(BaseModel):
    result: list[NetworkInterface] = Field(default_factory=list)


class QemuNetworkResponse(BaseModel):
    data: QemuNetworkData

