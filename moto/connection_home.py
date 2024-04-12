"""
Contains classes related to the representation of connection home
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Self

from influxdb_client import Point


@dataclass
class ConnectionHome:
    """
    A parsed connection home from the modem.
    """

    online: str
    status: str
    down_channels: int
    up_channels: int

    def to_point(self) -> Point:
        """
        Convert this object to an InfluxDB Point.
        """
        timestamp = datetime.now(timezone.utc)

        return (
            Point("connection")
            .time(timestamp)
            .tag("online", self.online)
            .tag("status", self.status)
            .tag("down_channels", self.down_channels)
            .tag("up_channels", self.up_channels)
        )

    @classmethod
    def from_response(cls, response: str) -> Self:
        """
        Parse the info to an object.
        """
        online = response["MotoHomeOnline"]
        status = response["GetHomeConnectionResult"]
        down_channels = int(response["MotoHomeDownNum"])
        up_channels = int(response["MotoHomeUpNum"])

        return cls(online, status, down_channels, up_channels)
