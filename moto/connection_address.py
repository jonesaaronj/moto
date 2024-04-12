"""
Contains classes related to the representation of connection home
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Self

from influxdb_client import Point

@dataclass
class ConnectionAddress:
    """
    A parsed connection address from the modem.
    """

    mac: str
    ipv4: str
    ipv6: str
    version: str
    result: str

    def to_point(self) -> Point:
        """
        Convert this object to an InfluxDB Point.
        """
        timestamp = datetime.now(timezone.utc)

        return (
            Point("connection")
            .time(timestamp)
            .tag("mac", self.mac)
            .tag("ipv4", self.ipv4)
            .tag("ipv6", self.ipv6)
            .tag("version", self.version)
            .tag("result", self.result)
        )

    @classmethod
    def from_response(cls, response: str) -> Self:
        """
        Parse the info to an object.
        """
        mac = response["MotoHomeMacAddress"]
        ipv4 = response["MotoHomeIpAddress"]
        ipv6 = response["MotoHomeIpv6Address"]
        version = response["MotoHomeSfVer"]
        result = response["GetHomeAddressResult"]

        return cls(mac, ipv4, ipv6, version, result)
