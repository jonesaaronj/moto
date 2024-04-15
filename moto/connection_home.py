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
            Point("connection_home")
            .time(timestamp)
            .field("online", self.online)
            .field("status", self.status)
            .field("down_channels", self.down_channels)
            .field("up_channels", self.up_channels)
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
