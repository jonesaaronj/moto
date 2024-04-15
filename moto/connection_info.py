"""
Contains classes related to the representation of connection info
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Self

from influxdb_client import Point


@dataclass
class ConnectionInfo:
    """
    A parsed connection info from the modem.
    """

    uptime_seconds: int
    network_access: str
    connection_status: str

    def to_point(self) -> Point:
        """
        Convert this object to an InfluxDB Point.
        """
        timestamp = datetime.now(timezone.utc)

        return (
            Point("connection_info")
            .time(timestamp)
            .field("uptime_seconds", self.uptime_seconds)
            .field("network_access", self.network_access)
            .field("connection_status", self.connection_status)
        )

    @classmethod
    def from_response(cls, response: str) -> Self:
        """
        Parse the info to an object.
        """
        uptime_seconds = cls.parse_uptime_seconds(response["MotoConnSystemUpTime"])
        network_access = response["MotoConnNetworkAccess"]
        connection_status = response["GetMotoStatusConnectionInfoResult"]

        return cls(uptime_seconds, network_access, connection_status)

    @classmethod
    def parse_uptime_seconds(cls, uptimeResponse: str) -> int:
        uptime = uptimeResponse.split()
        days = int(uptime[0])
        time = uptime[2]
        hour = int(time[0:2])
        minute = int(time[4:6])
        second = int(time[8:10])

        return second + (minute * 60) + (hour * 3600) + (days * 86400)
