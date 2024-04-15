"""
Command line interface.
"""
import logging
from time import sleep
from typing import Annotated

from rich.progress import Progress
from rich.table import Table
from schedule import every, run_pending
from typer import Typer
import typer

from .influx_client import InfluxClient
from .moto_client import MotoClient

app = Typer()
log = logging.getLogger("rich")


def _login(moto, progress: Progress):
    task = progress.add_task("Logging in...", total=None)
    moto.login()
    progress.update(task, total=1, completed=1)


def _get_logs(moto, progress):
    task = progress.add_task("Downloading logs...", total=None)
    logs = list(moto.get_logs())
    progress.update(task, total=1, completed=1)

    return logs


def _print_logs(logs, progress):
    table = Table(
        "timestamp"
        "level",
        "message",
        title="Logs",
    )
    for log in sorted(logs):
        table.add_row(
            str(log.timestamp),
            log.level,
            log.message,
        )

    progress.console.print(table)


def _ingest_logs(logs, influx, progress):
    task = progress.add_task("Ingesting logs...", total=len(logs))
    for l in logs:  # pylint: disable=invalid-name
        influx.ingest(l)
        progress.update(task, advance=1)


def _get_connection_info(moto, progress):
    task = progress.add_task("Downloading connection info...", total=None)
    info = moto.get_connection_info()
    progress.update(task, total=1, completed=1)
    return info


def _print_connection_info(info, progress):
    table = Table(
        "Uptime Seconds",
        "Network Access",
        "Connection Status",
        title="Connection Info",
    )

    table.add_row(
        str(info.uptime_seconds),
        info.network_access,
        info.connection_status,
    )

    progress.console.print(table)


def _ingest_connection_info(info, influx, progress):
    task = progress.add_task("Ingesting connection info...")
    influx.ingest(info)
    progress.update(task, total=1, completed=1)


def _get_connection_home(moto, progress):
    task = progress.add_task("Downloading connection home...", total=None)
    home = moto.get_connection_home()
    progress.update(task, total=1, completed=1)
    return home


def _print_connection_home(home, progress):
    table = Table(
        "Online",
        "Status",
        "Down Channels",
        "Up Channels",
        title="Connection Home",
    )

    table.add_row(
        home.online,
        home.status,
        str(home.down_channels),
        str(home.up_channels),
    )

    progress.console.print(table)


def _ingest_connection_home(home, influx, progress):
    task = progress.add_task("Ingesting connection home...")
    influx.ingest(home)
    progress.update(task, total=1, completed=1)


def _get_connection_address(moto, progress):
    task = progress.add_task("Downloading connection address...", total=None)
    address = moto.get_connection_address()
    progress.update(task, total=1, completed=1)
    return address


def _print_connection_address(address, progress):
    table = Table(
        "MAC",
        "IPV4",
        "IPV6",
        "Version",
        "Result",
        title="Connection Address",
    )

    table.add_row(
        address.mac,
        address.ipv4,
        address.ipv6,
        address.version,
        address.result,
    )

    progress.console.print(table)


def _ingest_connection_address(address, influx, progress):
    task = progress.add_task("Ingesting connection address...")
    influx.ingest(address)
    progress.update(task, total=1, completed=1)


def _get_downstream_channels(moto, progress):
    task = progress.add_task("Downloading downstream channels...", total=None)
    channels = list(moto.get_downstream_channels())
    progress.update(task, completed=True)

    return channels


def _ingest_downstream_channels(channels, influx, progress):
    task = progress.add_task("Ingesting downstream channels...", total=len(channels))
    for channel in channels:
        influx.ingest(channel)
        progress.update(task, advance=1)


def _get_upstream_channels(moto, progress):
    task = progress.add_task("Downloading upstream channels...", total=None)
    channels = list(moto.get_upstream_channels())
    progress.update(task, completed=True)

    return channels


def _ingest_upstream_channels(channels, influx, progress):
    task = progress.add_task("Ingesting upstream channels...", total=len(channels))
    for channel in channels:
        influx.ingest(channel)
        progress.update(task, advance=1)


def _print_downstream_channels(channels, progress):
    table = Table(
        "Channel",
        "Lock Status",
        "Modulation",
        "Channel ID",
        "Frequency",
        "Power",
        "SNR",
        "Corrected",
        "Uncorrected",
        title="Downstream Channels",
    )

    for channel in sorted(channels):
        table.add_row(
            str(channel.channel),
            channel.lock_status,
            channel.modulation,
            str(channel.channel_id),
            str(channel.frequency),
            str(channel.power),
            str(channel.snr),
            str(channel.corrected),
            str(channel.uncorrected),
        )

    progress.console.print(table)


def _print_upstream_channels(channels, progress):
    table = Table(
        "Channel",
        "Lock Status",
        "Channel Type",
        "Channel ID",
        "Symbol Rate",
        "Frequency",
        "Power",
        title="Upstream Channels",
    )

    for channel in sorted(channels):
        table.add_row(
            str(channel.channel),
            channel.lock_status,
            channel.channel_type,
            str(channel.channel_id),
            str(channel.symbol_rate),
            str(channel.frequency),
            str(channel.power),
        )

    progress.console.print(table)


@app.command()
def read(
    info: Annotated[bool, typer.Option("--info")] = False,
    logs: Annotated[bool, typer.Option("--logs")] = False
):
    """
    Read logs and levels from the modem and ingest them into InfluxDB.
    """
    influx = InfluxClient()
    moto = MotoClient()

    with Progress() as progress:
        _login(moto, progress)

        if info:
            home = _get_connection_home(moto, progress)
            _ingest_connection_home(home, influx, progress)

            info = _get_connection_info(moto, progress)
            _ingest_connection_info(info, influx, progress)

            address = _get_connection_address(moto, progress)
            _ingest_connection_address(address, influx, progress)

        channels = _get_downstream_channels(moto, progress)
        _ingest_downstream_channels(channels, influx, progress)

        channels = _get_upstream_channels(moto, progress)
        _ingest_upstream_channels(channels, influx, progress)

        if logs:
            logs = _get_logs(moto, progress)
            _ingest_logs(logs, influx, progress)


@app.command()
def dump(
    info: Annotated[bool, typer.Option("--info")] = False,
    logs: Annotated[bool, typer.Option("--logs")] = False
):
    """
    Read levels from the modem and print them to the console.
    """
    moto = MotoClient()

    with Progress() as progress:
        _login(moto, progress)

        if info:
            home = _get_connection_home(moto, progress)
            _print_connection_home(home, progress)

            info = _get_connection_info(moto, progress)
            _print_connection_info(info, progress)

            address = _get_connection_address(moto, progress)
            _print_connection_address(address, progress)

        channels = _get_downstream_channels(moto, progress)
        _print_downstream_channels(channels, progress)

        channels = _get_upstream_channels(moto, progress)
        _print_upstream_channels(channels, progress)

        if logs:
            logs = _get_logs(moto, progress)
            _print_logs(logs, progress)


def _ingest(info: bool = False, logs: bool = False):
    influx = InfluxClient()
    moto = MotoClient()

    try:
        log.info("logging in")

        moto.login()
    except:  # pylint: disable=bare-except
        log.exception("failed to log in")

    if info:
        try:
            log.info("getting connection info")
            info = moto.get_connection_info()
            influx.ingest(info)
        except:  # pylint: disable=bare-except
            log.exception("failed to get connection info")

        try:
            log.info("getting connection home")
            home = moto.get_connection_home()
            influx.ingest(home)
        except:  # pylint: disable=bare-except
            log.exception("failed to get connection home")

        try:
            log.info("getting connection address")
            address = moto.get_connection_address()
            influx.ingest(address)
        except:  # pylint: disable=bare-except
            log.exception("failed to get connection address")

    try:
        log.info("getting downstream channels")
        for channel in moto.get_downstream_channels():
            influx.ingest(channel)
    except:  # pylint: disable=bare-except
        log.exception("failed to get downstream channels")

    try:
        log.info("getting upstream channels")
        for channel in moto.get_upstream_channels():
            influx.ingest(channel)
    except:  # pylint: disable=bare-except
        log.exception("failed to get upstream channels")

    if logs:
        try:
            log.info("getting logs")
            for l in moto.get_logs():  # pylint: disable=invalid-name
                influx.ingest(l)
        except:  # pylint: disable=bare-except
            log.exception("failed to get logs")

@app.command()
def run(
    info: Annotated[bool, typer.Option("--info")] = False,
    logs: Annotated[bool, typer.Option("--logs")] = False
):
    """
    Run forever, reading periodically and ingesting to InfluxDB.
    """
    every().minute.do(lambda: _ingest(info, logs))

    while True:
        run_pending()
        sleep(1)
